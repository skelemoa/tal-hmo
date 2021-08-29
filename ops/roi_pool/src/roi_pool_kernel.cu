#include <ATen/ATen.h>
#include <ATen/cuda/CUDAContext.h>
#include <THC/THCAtomics.cuh>

#define CUDA_1D_KERNEL_LOOP(i, n)                            \
  for (int i = blockIdx.x * blockDim.x + threadIdx.x; i < n; \
       i += blockDim.x * gridDim.x)

#define THREADS_PER_BLOCK 1024

inline int GET_BLOCKS(const int N) {
  int optimal_block_num = (N + THREADS_PER_BLOCK - 1) / THREADS_PER_BLOCK;
  int max_block_num = 65000;
  return min(optimal_block_num, max_block_num);
}

template <typename scalar_t>
__global__ void ROIPoolForward(const int nthreads, const scalar_t *bottom_data,
                               const scalar_t *rois,
                               const scalar_t spatial_scale, const int channels,
                                const int width,
                               const int pooled_w,
                               scalar_t *top_data, int *argmax_data) {
  CUDA_1D_KERNEL_LOOP(index, nthreads) {
    // (n, c, pw) is an element in the pooled output
    int pw = index % pooled_w;
    // int ph = (index / pooled_w) % pooled_h;
    int c = (index / pooled_w ) % channels;
    int n = index / pooled_w / channels;

    const scalar_t *offset_rois = rois + n * 3;
    int roi_batch_ind = offset_rois[0];
    // calculate the roi region on feature maps
    scalar_t roi_x1 = offset_rois[1] * spatial_scale;
    scalar_t roi_x2 = (offset_rois[2] + 1) * spatial_scale;

    // force malformed rois to be 1x1
    scalar_t roi_w = roi_x2 - roi_x1;
    if (roi_w <= 0 ) continue;

    scalar_t bin_size_w = roi_w / static_cast<scalar_t>(pooled_w);

    // the corresponding bin region
    int bin_x1 = floor(static_cast<scalar_t>(pw) * bin_size_w + roi_x1);
    int bin_x2 = ceil(static_cast<scalar_t>(pw + 1) * bin_size_w + roi_x1);

    // add roi offsets and clip to input boundaries
    bin_x1 = min(max(bin_x1, 0), width);
    bin_x2 = min(max(bin_x2, 0), width);
    bool is_empty = (bin_x2 <= bin_x1);

    // If nothing is pooled, argmax = -1 causes nothing to be backprop'd
    int max_idx = -1;
    bottom_data += (roi_batch_ind * channels + c)  * width;

    // Define an empty pooling region to be zero
    scalar_t max_val = is_empty ? static_cast<scalar_t>(0)
                                : bottom_data[bin_x1] - 1;

    
    for (int w = bin_x1; w < bin_x2; ++w) {
        int offset = w;
        if (bottom_data[offset] > max_val) {
          max_val = bottom_data[offset];
          max_idx = offset;
        }
      
    }
    top_data[index] = max_val;
    if (argmax_data != NULL) argmax_data[index] = max_idx;
  }
}

int ROIPoolForwardLaucher(const at::Tensor features, const at::Tensor rois,
                          const float spatial_scale, const int channels,
                          const int width, const int num_rois,
                          const int pooled_w,
                          at::Tensor output, at::Tensor argmax) {
  const int output_size = num_rois * channels * pooled_w;

  AT_DISPATCH_FLOATING_TYPES_AND_HALF(
      features.scalar_type(), "ROIPoolLaucherForward", ([&] {
        const scalar_t *bottom_data = features.data<scalar_t>();
        const scalar_t *rois_data = rois.data<scalar_t>();
        scalar_t *top_data = output.data<scalar_t>();
        int *argmax_data = argmax.data<int>();

        ROIPoolForward<scalar_t><<<GET_BLOCKS(output_size), THREADS_PER_BLOCK,
                                   0, at::cuda::getCurrentCUDAStream()>>>(
            output_size, bottom_data, rois_data, scalar_t(spatial_scale),
            channels, width, pooled_w, top_data, argmax_data);
      }));
  THCudaCheck(cudaGetLastError());
  return 1;
}
template <typename scalar_t>
__global__ void ROIPoolBackward(const int nthreads, const scalar_t *top_diff,
                                const scalar_t *rois, const int *argmax_data,
                                const scalar_t spatial_scale,
                                const int channels,
                                const int width,
                                const int pooled_w, scalar_t *bottom_diff) {
  CUDA_1D_KERNEL_LOOP(index, nthreads) {
    int pw = index % pooled_w;
    // int ph = (index / pooled_w) % pooled_h;
    int c = (index / pooled_w ) % channels;
    int n = index / pooled_w  / channels;
    int roi_batch_ind = rois[n * 3];
    int bottom_index = argmax_data[(n * channels + c) * pooled_w + pw];
    if (bottom_index != -1) {
      atomicAdd(bottom_diff + (roi_batch_ind * channels + c) * width +
                    bottom_index,
                top_diff[index]);
    }
  }
}
int ROIPoolBackwardLaucher(const at::Tensor top_grad, const at::Tensor rois,
                           const at::Tensor argmax, const float spatial_scale,
                           const int batch_size, const int channels,
                            const int width,
                           const int num_rois,
                           const int pooled_w, at::Tensor bottom_grad) {
  const int output_size = num_rois * pooled_w * channels;
  AT_DISPATCH_FLOATING_TYPES_AND_HALF(
      top_grad.scalar_type(), "ROIPoolLaucherBackward", ([&] {
        const scalar_t *top_diff = top_grad.data<scalar_t>();
        const scalar_t *rois_data = rois.data<scalar_t>();
        const int *argmax_data = argmax.data<int>();
        scalar_t *bottom_diff = bottom_grad.data<scalar_t>();
        if (sizeof(scalar_t) == sizeof(double)) {
          fprintf(stderr, "double is not supported\n");
          exit(-1);
        }
        ROIPoolBackward<scalar_t><<<GET_BLOCKS(output_size), THREADS_PER_BLOCK,
                                    0, at::cuda::getCurrentCUDAStream()>>>(
            output_size, top_diff, rois_data, argmax_data,
            scalar_t(spatial_scale), channels, width,
            pooled_w, bottom_diff);
      }));
  THCudaCheck(cudaGetLastError());
  return 1;
}