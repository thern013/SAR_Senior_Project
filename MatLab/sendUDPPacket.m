function sendUDPPacket(iqBytes, fs)
    % Define UDP target
    udpIP = '127.0.0.1'; % Change if sending to another device
    udpPort = 5000;      % GNU Radio listening port
    packetSize = 1472;   % Packet size in bytes
    
    % Create UDP object
    udpObj = udpport("Datagram", "IPV4");
    udpObj.ByteOrder = "little-endian"; % Ensure compatibility with GNU Radio
    
    % Send packets in chunks of 1472 bytes
    for i = 1:packetSize:length(iqBytes)
        packet = iqBytes(i:min(i+packetSize-1, end));
        write(udpObj, packet, udpIP, udpPort);
        pause((1 / fs) * (packetSize / 8)); % Control transmission rate
    end
    
    disp("Complex packets sent to GNU Radio.");
    
    % Clean up
    clear udpObj;
end
