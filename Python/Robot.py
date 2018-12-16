from scipy.io import wavfile
import numpy as np

# define necessary utility functions
def build_sine_table(f_sine, samp_freq, data_type=16):
    """
    :param f_sine: Modulate frequency for voice effect in Hz.
    :param samp_freq: Sampling frequency in Hz
    :param data_type: Data type of sinusoid table. Must be either uint16 (default) or uint32.
    :return:
    """

    if data_type!=16 and data_type!=32:
        data_type = 16

    # periods
    samp_per = 1./samp_freq
    sine_per = 1./f_sine

    # compute time instances
    t_vals = np.arange(0, sine_per, samp_per)
    LOOKUP_SIZE = len(t_vals)
    n_vals = np.arange(LOOKUP_SIZE)

    # compute the sine table
    MAX_SINE = 2**(data_type-1)-1
    w_mod = 2*np.pi*f_sine/samp_freq
    SINE_TABLE = np.sin(w_mod*n_vals) * MAX_SINE

    return SINE_TABLE, MAX_SINE, LOOKUP_SIZE

# parameters
buffer_len = 256

# test signal
input_wav = "speech.wav"
samp_freq, signal = wavfile.read(input_wav)
signal = signal[:,]  # get first channel
n_buffers = len(signal)//buffer_len
data_type = signal.dtype

print("Sampling frequency : %d Hz" % samp_freq)
print("Data type          : %s" % signal.dtype)

# allocate input and output buffers
input_buffer = np.zeros(buffer_len, dtype=data_type)
output_buffer = np.zeros(buffer_len, dtype=data_type)

# state variables
def init():
    global sine_pointer
    global x_prev
    global GAIN
    global SINE_TABLE
    global MAX_SINE
    global LOOKUP_SIZE

    GAIN = 1
    x_prev = 0
    sine_pointer = 0

    # compute SINE TABLE
    vals = build_sine_table(100, samp_freq, data_type=16)
    SINE_TABLE = vals[0]
    MAX_SINE = vals[1]
    LOOKUP_SIZE = vals[2]

# the process function!
def process(input_buffer, output_buffer, buffer_len):

    global x_prev
    global sine_pointer

    for n in range(buffer_len):

        # high pass filter
        output_buffer[n] = input_buffer[n] - x_prev

        # modulation
        output_buffer[n] = (output_buffer[n]*SINE_TABLE[sine_pointer])/MAX_SINE

        # update state variables
        sine_pointer = (sine_pointer + 1) % LOOKUP_SIZE
        x_prev = input_buffer[n]
"""
Nothing to touch after this!
"""
init()
# simulate block based processing
signal_proc = np.zeros(n_buffers*buffer_len, dtype=data_type)
for k in range(n_buffers):

    # index the appropriate samples
    input_buffer = signal[k*buffer_len:(k+1)*buffer_len]
    process(input_buffer, output_buffer, buffer_len)
    signal_proc[k*buffer_len:(k+1)*buffer_len] = output_buffer

# write to WAV
wavfile.write("speech_mod.wav", samp_freq, signal_proc)