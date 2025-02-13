function plotSignal(complexSignal, fs)
    % fs: Sampling frequency (in Hz)
    
    % Time axis based on sampling frequency and signal length
    N = length(complexSignal);  % Number of samples
    t = (0:N-1) / fs;           % Time vector in seconds
    
    % Convert time to milliseconds
    t_ms = t * 1000;  % Multiply by 1000 to convert to milliseconds
    
    % Extract real, imaginary components
    realPart = real(complexSignal);
    imagPart = imag(complexSignal);
    
    % Compute FFT of the complex signal
    fftSignal = fft(complexSignal);
    
    % Shift zero frequency to center of FFT (for visualization)
    fftSignalShifted = fftshift(fftSignal);
    
    % Create the frequency axis for FFT (centered at 0Hz)
    fftFreq = (-N/2:N/2-1) * (fs / N);  % Frequency axis in Hz
    
    % Calculate the magnitude of the FFT
    fftMagnitude = abs(fftSignalShifted);  
    
    % Create a figure
    figure;
    
    % Plot the real and imaginary parts in the same graph (0 to 30 milliseconds)
    subplot(2, 1, 1);  % 2 rows, 1 column, 1st plot
    timeLimit = 1000;  % Set time limit to 1000 milliseconds
    plot(t_ms(1:min(end, fs * timeLimit / 1000)), realPart(1:min(end, fs * timeLimit / 1000)), 'b', 'DisplayName', 'Real Part');
    hold on;
    plot(t_ms(1:min(end, fs * timeLimit / 1000)), imagPart(1:min(end, fs * timeLimit / 1000)), 'r', 'DisplayName', 'Imaginary Part');
    hold off;
    title('Real and Imaginary Parts of Complex Signal');
    xlabel('Time (milliseconds)');
    ylabel('Amplitude');
    legend;
    
    % Plot the centered FFT of the complex signal
    subplot(2, 1, 2);  % 2 rows, 1 column, 2nd plot
    plot(fftFreq, fftMagnitude, 'g');
    title('Centered FFT of Complex Signal');
    xlabel('Frequency (Hz)');
    ylabel('Magnitude');
end
