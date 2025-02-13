fs = 32000;  % Sampling frequency
f = 5;      % Sine wave frequency
matlabOutputFile = "gnuFileDump/matlabChirp.dat";

% Generate chirp signal
outputSignal = generateChirp(fs, f);
% Call the plot function to display the real, imaginary, and magnitude plots
plotSignal(rxSignal, fs);

% % Send the UDP packet
% sendUDPPacket(iqBytes, fs);

% Write the complex signal to a file (file is cleared first)
writeSignalToFile(outputSignal, matlabOutputFile);

gnuInputFile = 'gnuFileDump/gnuIQRx.exe';  % Update with your file's location
rxSignal = readFile(gnuInputFile);

% Call the plot function to display the real, imaginary, and magnitude plots
plotSignal(rxSignal, fs);
