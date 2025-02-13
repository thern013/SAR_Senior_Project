function receiveUDPPacket(timeout)
    % Define UDP parameters
    udpPort = 8080;   % Listening port
    packetSize = 1472; % Packet size in bytes

    % Create UDP receiver object
    udpObj = udpport("Datagram", "IPV4", "LocalPort", udpPort);
    udpObj.ByteOrder = "little-endian"; % Match sender's format
    udpObj.Timeout = timeout; % Set timeout (in seconds)

    disp("Waiting for a UDP packet on port " + udpPort + "...");

    try
        % Attempt to read data from the UDP port
        data = read(udpObj, packetSize, "uint8");  % Receive data (complex float32 format)
        
        if ~isempty(data)
            % Convert received bytes to float32
            rawData = data.Data
            iqSignal = typecast(rawData, 'single');
            
            % Extract real and imaginary parts (complex signal)
            realPart = iqSignal(1:2:end);
            imagPart = iqSignal(2:2:end);
            complexSignal = realPart + 1j * imagPart;

            % Display the first few received samples
            disp("Received data (first 10 complex samples):");
            disp(complexSignal(1:min(10, length(complexSignal))));
        else
            disp("No data received within the timeout.");
        end
    catch exception
        % Handle timeout or errors
        disp("Error receiving data: " + exception.message);
    end

    % Clean up UDP object
    delete(udpObj);
end
