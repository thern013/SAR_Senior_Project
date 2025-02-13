function writeSignalToFile(complexSignal, filename)
    % This function takes a complex signal and writes it to a file, 
    % ensuring the file is cleared before writing.
    % Input:
    %   complexSignal - A vector of complex numbers (e.g., output from a receiver).
    %   filename      - The name of the file to save the signal to.
    
    % Ensure the file is cleared before writing
    if exist(filename, 'file') == 2
        delete(filename); % Delete the file if it exists
    end
    
    % Open the file in write mode ('w')
    fileID = fopen(filename, 'w');
    
    if fileID == -1
        error('Failed to open file for writing.');
    end
    
    % Separate the real and imaginary parts of the complex signal
    realPart = real(complexSignal);
    imagPart = imag(complexSignal);
    
    % Write real and imaginary parts to the file (interleaved)
    fwrite(fileID, realPart, 'float32');  % Write real part as float32
    fwrite(fileID, imagPart, 'float32');  % Write imaginary part as float32
    
    % Close the file
    fclose(fileID);
    
    disp(['Signal written to file: ', filename]);
end
