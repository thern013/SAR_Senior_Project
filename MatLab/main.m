 Set parameters
f0 = 80e6;        % Frequency of the signal (80 MHz)
f1 = 80e6;        % Same frequency for a CW signal
fs = 20 * f1;     % Sample rate (20 times the signal frequency)
d = 1e-6;         % Duration of the chirp signal

% Initialize the ChirpSignal object
chripObj = ChirpSignal(f0, f1, d);
signal = chripObj.txLoopChirp(1);  % Generate the CW signal (80 MHz)
b200Obj = B200(f0, f1);            % Initialize the B200 object
b200Obj = b200Obj.run(signal);     % Transmit and receive the signal
b200Obj.plot(b200Obj.rxSignal);