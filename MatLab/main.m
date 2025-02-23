% Parameters for the chirp
f_start = 0;   % Start frequency in Hz (2.4 GHz)
f_end = 50;    % End frequency in Hz (2.48 GHz)
duration = 1e-0;   % Duration in seconds (10 us)

% Create the chirp signal object
chirpObj = ChirpSignal(f_start, f_end, duration);
txSignal = chirpObj.createTxInstance();
rxSignal = chirpObj.createRxInstance();
chirpObj.calculateDistance(txSignal, rxSignal)

