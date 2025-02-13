function complexSignal = readFile(filePath)
    % Read binary data from a file and return it as a complex signal
    
    % Open the file for reading
    fid = fopen(filePath, 'rb');
    
    if fid == -1
        error('Error opening file: %s', filePath);
    end
    
    % Read the binary data (assuming complex float32 format)
    % Two consecutive float32 values represent one complex number (real and imaginary parts)
    data = fread(fid, 'float32');  % Read as float32
    
    % Close the file
    fclose(fid);
    
    % Check if the data length is even (as we are expecting pairs for complex numbers)
    if mod(length(data), 2) ~= 0
        error('The data in the file is not in pairs for complex numbers.');
    end
    
    % Reconstruct the complex signal (real + j*imaginary)
    realPart = data(1:2:end);       % Extract real part
    imagPart = data(2:2:end);       % Extract imaginary part
    complexSignal = realPart + 1j * imagPart;  % Combine into a complex signal
    
    % Display a message that data has been successfully read
    disp('Data successfully read from file and converted to complex signal.');
end
