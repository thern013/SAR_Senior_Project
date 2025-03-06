classdef ChirpSignal
    % ChirpSignal Class to represent a complex chirp signal
    %   This class holds the parameters and the generated signal for a chirp
    
    properties
        f_start  % Start frequency in Hz
        f_end    % End frequency in Hz
        fs       % Sample rate in Hz
        duration % Duration of the chirp signal in seconds
        t        % Time vector
        signal   % The generated complex chirp signal
    end
    
    methods
        % Constructor method
        function obj = ChirpSignal(f_start, f_end, duration)
            % Constructor for ChirpSignal class
            if nargin > 0
                obj.f_start = f_start;
                obj.f_end = f_end;
                obj.fs = 20 * f_end;
                obj.duration = duration;
                obj.t = single(0:1/obj.fs:obj.duration);  % Time vector
                obj.signal = obj.generateChirpSignal();  % Generate the chirp signal
            end
        end
        
        % Method to generate the complex chirp signal
        function signal = generateChirpSignal(obj)
            % Generate the complex chirp signal using MATLAB's chirp function
            ph0 = 0;  % Initial phase
            % signal = chirp(obj.t, obj.f_start, obj.t(end), obj.f_end, "linear", ph0, "complex");
            signal = chirp(obj.t, obj.f_start, obj.t(end), obj.f_end);
        end
        
        % Method to plot the real and imaginary parts of the chirp signal
        function plotSignal(obj)
            figure;
            
            % Plot Real Part
            subplot(3, 1, 1);
            plot(obj.t, real(obj.signal));
            title('Real Part of the Complex Chirp Signal');
            xlabel('Time (s)');
            ylabel('Amplitude');
            grid on;
            
            % Plot Imaginary Part
            subplot(3, 1, 2);
            plot(obj.t, imag(obj.signal));
            title('Imaginary Part of the Complex Chirp Signal');
            xlabel('Time (s)');
            ylabel('Amplitude');
            grid on;

            subplot(3,1,3);
            pspectrum(obj.signal, obj.t, "spectrogram", ...
                "TimeResolution", obj.duration / 10, ...  % Adjust time resolution
                "OverlapPercent", 50, ...  % Adjust overlap
                "Leakage", 0.85, ...
                "FrequencyLimits", [obj.f_start, obj.f_end]);  % Limit frequency range from 2.4 GHz to 2.48 GHz
        end
        
        % Method to return the signal
        function signal = getSignal(obj)
            signal = obj.signal;
        end
        
        function nullSignal = createNullSignal(obj)
            nullSignal = single(zeros(1, length(obj.t)));
        end
        
        function txSignal = createTxInstance(obj)
            nullSignal = obj.createNullSignal();
            txSignal = [obj.signal nullSignal];
        end

        function txSignal = txLoopChirp(obj, loops)
            loopingTxSignal = obj.createTxInstance;

            for i = 1:loops
                loopingTxSignal = [loopingTxSignal obj.createTxInstance]; %#ok<AGROW>
            end

            txSignal = loopingTxSignal;           
        end

        function randomChirpLength = createRandomizedChirpLength(~)
            randomChirpLength = randi([1, 1001]);
        end

        function rxSignal = createRxInstance(obj)
            randomTime = obj.createRandomizedChirpLength();
            nullSignal = obj.createNullSignal;
            rxNullInit = nullSignal(1:randomTime);
            rxNullAfterInit = nullSignal(randomTime:end);
            rxSignal = [rxNullInit obj.signal rxNullAfterInit];

            obj.graphRealSignal(rxSignal);
        end

        function calculateDistance(obj, txSignal, rxSignal)
            rxChirpTime = find(rxSignal, 1, 'first');
            txChirpTime = find(txSignal, 1, 'first');
            disp(['rxTime: ', num2str(rxChirpTime)]);
            disp(['tx Time: ', num2str(txChirpTime)]);            
        end

        function graphRealSignal(obj, Signal)
            totalLength = length(Signal);  % This will be 2002
            fullTime = linspace(0, totalLength / obj.fs, totalLength);  % Adjust time vector based on total length
            
            % Plot the concatenated signal with the adjusted time vector
            figure;
            plot(fullTime, Signal);
            title('Chirp Signal');
            xlabel('Time (s)');
            ylabel('Amplitude');
            grid on;
        end            
    end
end
