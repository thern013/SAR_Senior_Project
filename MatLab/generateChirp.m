function iqBytes = generateChirp(fs, f)
    % Generate a complex sine wave and return it as float32 interleaved bytes
    duration = 5;  % Duration in seconds
    % Time vector
    t = linspace(0, duration, fs * duration);

    % Generate complex sine wave
    complexWave = exp(1j * 2 * pi * f * t); % e^(j2πft) = cos(2πft) + j*sin(2πft)

    % Convert to interleaved float32 bytes
    iqData = single([real(complexWave); imag(complexWave)]);
    iqBytes = typecast(iqData(:), 'uint8'); % Convert to bytes

    disp("Complex wave created");
end
