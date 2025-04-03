import { UntypedFormBuilder } from "@angular/forms";
import { AudioData } from "./AudioData";
import { error } from "console";

export class AudioDataProvider {
    private sampleRateProperty: number;
    private bufferSizeProperty: number; // should be with power of 2 for correct work of FFT

    private audioContext?: AudioContext | null = null;
    private inputPoint?: GainNode | null = null;
    private streamSource?: MediaStreamAudioSourceNode| null = null;
    private analyserNode?: AnalyserNode | null = null;
    private zeroGain?: GainNode | null = null ;

    private initializedProperty = false;
    private isDeletedProperty = false;

    private audioData?: AudioData;

    private time = 0;

    private freqByteData?: Uint8Array | undefined;

    public permissionError?: boolean | undefined;

    constructor(sampleRate: number, bufferSizeProperty: number) {
        this.sampleRateProperty = sampleRate;
        this.bufferSizeProperty = bufferSizeProperty;
        this.audioData = new AudioData(bufferSizeProperty);
    }

    public get initialized() {
        return this.initializedProperty;
    }

    public get isDeleted() {
        return this.isDeletedProperty;
    }

    public get bufferSize() {
        return this.bufferSizeProperty;
    }

    public get sampleRate() {
        return this.sampleRateProperty;
    }

    public async initAudio() {
        try {
            const constraints = { audio: true, video: false };
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            // @ts-ignore
            const AudioContextClass: any = window.AudioContext || window.webkitAudioContext || false;
            if (AudioContextClass) {
                this.audioContext = new AudioContextClass();
            } else {
                throw Error("AudioContextClass is not defined");
            }

            this.inputPoint = this.audioContext?.createGain();

            // Create an AudioNode from the stream.
            this.streamSource = this.audioContext!.createMediaStreamSource(stream);
            this.streamSource.connect(this.inputPoint!);

            this.analyserNode = this.audioContext?.createAnalyser();
            this.analyserNode!.fftSize = this.bufferSizeProperty * 2;
            this.inputPoint!.connect(this.analyserNode!);

            this.zeroGain = this.audioContext!.createGain();
            this.zeroGain.gain.value = 0.0;
            this.inputPoint!.connect(this.zeroGain);
            this.zeroGain.connect(this.audioContext!.destination);

            this.freqByteData = new Uint8Array(this.analyserNode!.frequencyBinCount);

            this.initializedProperty = true;
            return true;
        } catch (error) {
            //@ts-ignore
            if (error.name === "NotAllowedError") {
                this.permissionError = true;
            }
            console.warn("Error getting audio", error);
            return false;
        }
    }

    public closeAudio() {
        this.audioContext?.close();
        this.audioContext = null;
        this.inputPoint = null;
        this.streamSource = null;
        this.zeroGain = null;
        this.audioData = undefined;
        this.freqByteData = undefined;
        this.initializedProperty = false;
        this.isDeletedProperty = true;
    }

    public next(socketData: Int16Array) {
        if (this.initialized === false) {
            throw new Error("Data provider isn't initialized!");
        }
        let customData

        if (socketData.length !== 0) {
            customData = Array.from(socketData);
        }
        else {
            customData = Array.from( {length: this.bufferSizeProperty }, () => 0);
        }

        // Generate a random array of values between -32768 and 32767
        // customData = Array.from({ length: this.bufferSizeProperty }, () => 
        //     Math.floor(Math.random() * 65536) - 32768
        // );
        this.analyserNode!.getByteTimeDomainData(this.freqByteData!);

        for (let i = 0; i < customData.length; i++) {
            this.audioData!.xData[i] = this.time++;
            this.audioData!.yData[i] = customData![i];
        }
    
        return this.audioData;
    }
    
}
