classdef B200
    % B200 Class to represent the USRP device and handle trigger-based transmit and receive
    
    properties
        platform
        address
        USRPGain
        USRPCenterFrequency
        sampleRate
        triggerTime
        txStruct
        rxStruct
        rxSignal % Property to store received signal
        
    end
    
    methods
        % Constructor method
        function obj = B200(f_start, f_end)
            % Constructor for B200 class
            if nargin > 0
                obj.platform = "B200";
                obj.address  = '30FD82A';
                obj.USRPGain = 35;  % Set USRP radio gain
                obj.USRPCenterFrequency = (f_start + f_end) / 2;  % Set USRP radio center frequency
                obj.sampleRate = f_end * 2;  % Sample rate of transmitted signal
                obj.triggerTime = 1;
                obj.txStruct = comm.SDRuTransmitter( ...
                    'Platform', obj.platform, ...
                    'SerialNum', obj.address, ...
                    'ChannelMapping', 1, ...
                    'CenterFrequency', obj.USRPCenterFrequency, ...
                    'Gain', obj.USRPGain, ...
                    'MasterClockRate', 32000000, ...
                    'InterpolationFactor', 512, ...
                    'TransportDataType', 'int16', ...
                    'EnableTimeTrigger', true, ...  % Enable time-triggered transmission
                    'TriggerTime', obj.triggerTime);  % Set trigger time for transmission (1 ms)
                
                obj.rxStruct = comm.SDRuReceiver( ...
                    'Platform', obj.platform, ...
                    'SerialNum', obj.address, ...
                    'ChannelMapping', 1, ...
                    'CenterFrequency', obj.USRPCenterFrequency, ...
                    'Gain', obj.USRPGain, ...
                    'MasterClockRate', 32000000, ...
                    'DecimationFactor', 512, ...
                    'TransportDataType', 'int16', ...
                    'EnableTimeTrigger', true, ...  % Enable time-triggered reception
                    'TriggerTime', obj.triggerTime);  % Set trigger time for reception (1 ms)
            end
        end

        % Run method to transmit and receive the signal
        function obj = run(obj, signal)
            % Transmit and receive the signal with time triggering
            obj.transmit(signal);  % Transmit the signal
            obj.rxSignal = obj.recieve();  % Receive the signal and store it in the object
        end

        % Convert row vector to column vector
        function columnVec = rowToColumnVec(obj, rowVec)
            columnVec = rowVec';    % Convert to Mx1 column vector
        end

        % Transmit the signal
        function transmit(obj, signal)
            signal = obj.rowToColumnVec(signal);  % Convert the signal to a column vector
            obj.txStruct(signal);  % Transmit the signal with time trigger
        end

        % Receive the signal
        function rxSignal = recieve(obj)
            currentTime = obj.rxStruct.getTimeNow;  % Query current USRP time
            trigTime = currentTime + 0.001;  % Add a small offset (1 ms) to current time
            
            % Set the trigger time for the receiver
            obj.rxStruct.TriggerTime = trigTime;

            % Receive the signal with time trigger
            rxSignal = obj.rxStruct();  % Receive the signal using the configured receiver
        end

        function plot(obj)
            % Plot the signal
            figure;
            plot(t, signal);
            title('80 MHz Continuous Wave (CW) Signal');
            xlabel('Time (seconds)');
            ylabel('Amplitude');
            grid on;
            
            % Set x-axis limits to cover 5 full periods (62.5 ns)
            xlim([0 62.5e-9]);
        end
    end
end
