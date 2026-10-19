// NAM loudness, as the NAM trainer writes it into a model's metadata: the RMS in dB of the model's output for
// loudness_input.wav (from neural-amp-modeler, 48 kHz). Backline levels models by it (-18 dB), so models without it
// jump in volume. Prints "<dB>\t<file>" per model.
//   g++ -O2 -std=c++20 -DNAM_SAMPLE_FLOAT -I$NAM -I$NAM/Dependencies/eigen -I$NAM/Dependencies/nlohmann \
//       loudness.cpp $NAM/NAM/*.cpp -o loudness
#include "NAM/get_dsp.h"
#include <cmath>
#include <cstdio>
#include <fstream>
#include <iterator>
#include <vector>

// 24-bit mono PCM WAV, as loudness_input.wav is
static std::vector<float> readWav(const char* path)
{
    std::ifstream f(path, std::ios::binary);
    std::vector<unsigned char> b((std::istreambuf_iterator<char>(f)), {});
    size_t i = 12;
    while (i + 8 <= b.size())
    {
        const unsigned size = b[i + 4] | b[i + 5] << 8 | b[i + 6] << 16 | (unsigned) b[i + 7] << 24;
        if (std::equal(b.begin() + (long) i, b.begin() + (long) i + 4, "data"))
        {
            std::vector<float> x;
            for (size_t k = i + 8; k + 2 < i + 8 + size; k += 3)
                x.push_back((float) ((int) ((unsigned) b[k] << 8 | (unsigned) b[k + 1] << 16 | (unsigned) b[k + 2] << 24) >> 8) / 8388608.0f);
            return x;
        }
        i += 8 + size + (size & 1);
    }
    return {};
}

int main(int argc, char** argv)
{
    auto x = readWav(argv[1]);
    for (int a = 2; a < argc; ++a)
    {
        auto dsp = nam::get_dsp(std::filesystem::path(argv[a]));
        const int block = 4096;
        dsp->Reset(48000.0, block);
        std::vector<float> y(x.size());
        for (size_t pos = 0; pos < x.size(); pos += block)
        {
            float* in = x.data() + pos;
            float* out = y.data() + pos;
            dsp->process(&in, &out, (int) std::min<size_t>(block, x.size() - pos));
        }
        double sum = 0;
        for (const float v : y)
            sum += (double) v * v;
        std::printf("%.4f\t%s\n", 10.0 * std::log10(sum / (double) y.size()), argv[a]);
    }
}
