"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { transcribeAudio } from "../../lib/api";

type RecordingState = "idle" | "requesting" | "recording" | "processing";

export default function VoicePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const appealType = searchParams.get("type") || "standard";

  const [state, setState] = useState<RecordingState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [duration, setDuration] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string>("");

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationRef = useRef<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const MAX_DURATION = 120; // 2 minutes in seconds

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopRecording();
      if (timerRef.current) clearInterval(timerRef.current);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [audioUrl]);

  // Auto-stop at max duration
  useEffect(() => {
    if (state === "recording" && duration >= MAX_DURATION) {
      stopRecording();
    }
  }, [duration, state]);

  const updateAudioLevel = useCallback(() => {
    if (analyserRef.current && state === "recording") {
      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
      analyserRef.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
      setAudioLevel(Math.min(100, (average / 128) * 100));
      animationRef.current = requestAnimationFrame(updateAudioLevel);
    }
  }, [state]);

  const startRecording = async () => {
    setError(null);
    setState("requesting");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
        },
      });

      streamRef.current = stream;

      // Setup audio analyzer for visual feedback
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      // Determine supported MIME type
      const mimeType = MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : MediaRecorder.isTypeSupported("audio/mp4")
        ? "audio/mp4"
        : "audio/wav";

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunksRef.current, { type: mimeType });
        setAudioBlob(blob);
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        setState("idle");
      };

      mediaRecorder.start(1000); // Collect data every second
      setState("recording");
      setDuration(0);

      // Start duration timer
      timerRef.current = setInterval(() => {
        setDuration((d) => d + 1);
      }, 1000);

      // Start audio level animation
      updateAudioLevel();
    } catch (err) {
      console.error("Microphone access error:", err);
      setState("idle");

      if (err instanceof DOMException) {
        if (
          err.name === "NotAllowedError" ||
          err.name === "PermissionDeniedError"
        ) {
          setError(
            "Microphone access denied. Please allow microphone access in your browser settings."
          );
        } else if (err.name === "NotFoundError") {
          setError(
            "No microphone found. Please connect a microphone and try again."
          );
        } else {
          setError(`Microphone error: ${err.message}`);
        }
      } else {
        setError("Failed to access microphone. Please try again.");
      }
    }
  };

  const stopRecording = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }

    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    setAudioLevel(0);
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handleTranscribe = async () => {
    if (!audioBlob) return;

    setState("processing");
    setError(null);
    try {
      // Convert Blob to File for the API
      const audioFile = new File([audioBlob], "recording.webm", {
        type: audioBlob.type || "audio/webm",
      });
      const result = await transcribeAudio(audioFile);
      setTranscript(result.transcript || "");
      setError(null);
    } catch (err) {
      console.error("Transcription error:", err);
      setError(
        err instanceof Error
          ? err.message
          : "Transcription failed. You can type your appeal instead."
      );
    } finally {
      setState("idle");
    }
  };

  const handleContinue = () => {
    // TODO: Store transcript in state/context
    router.push(`/appeal/review?type=${appealType}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-2xl">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/appeal/camera"
            className="text-indigo-600 hover:text-indigo-700 font-medium"
          >
            ← Back
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mt-4">
            Record Your Story
          </h1>
          <p className="text-gray-600 mt-2">
            Step 3 of 5: Tell us what happened (up to 2 minutes)
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded mb-6">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Recording Interface */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-6">
          {!audioUrl ? (
            <div className="text-center">
              <div className="mb-6">
                <div
                  className={`mx-auto w-32 h-32 rounded-full flex items-center justify-center ${
                    state === "recording"
                      ? "bg-red-500 animate-pulse"
                      : "bg-indigo-100"
                  }`}
                >
                  {state === "recording" ? (
                    <svg
                      className="w-16 h-16 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                      <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                    </svg>
                  ) : (
                    <svg
                      className="w-16 h-16 text-indigo-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                      />
                    </svg>
                  )}
                </div>
              </div>

              {/* Audio Level Visualization */}
              {state === "recording" && (
                <div className="mb-4">
                  <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-indigo-600 transition-all duration-100"
                      style={{ width: `${audioLevel}%` }}
                    />
                  </div>
                </div>
              )}

              <div className="mb-6">
                {state === "recording" ? (
                  <div>
                    <p className="text-3xl font-bold text-red-600 mb-2">
                      {formatTime(duration)} / {formatTime(MAX_DURATION)}
                    </p>
                    <p className="text-gray-600">Recording in progress...</p>
                  </div>
                ) : state === "processing" ? (
                  <div>
                    <p className="text-lg text-gray-600">Processing...</p>
                  </div>
                ) : (
                  <p className="text-gray-600">
                    Click the button below to start recording
                  </p>
                )}
              </div>

              <button
                onClick={state === "recording" ? stopRecording : startRecording}
                disabled={state === "requesting" || state === "processing"}
                className={`px-8 py-4 rounded-lg font-semibold text-lg transition-colors disabled:opacity-50 ${
                  state === "recording"
                    ? "bg-red-600 hover:bg-red-700 text-white"
                    : "bg-indigo-600 hover:bg-indigo-700 text-white"
                }`}
              >
                {state === "recording"
                  ? "Stop Recording"
                  : state === "requesting"
                  ? "Requesting Access..."
                  : state === "processing"
                  ? "Processing..."
                  : "Start Recording"}
              </button>
            </div>
          ) : (
            <div className="text-center">
              <audio
                ref={audioRef}
                src={audioUrl}
                controls
                className="w-full mb-6"
              />
              <div className="flex gap-4 justify-center">
                <button
                  onClick={() => {
                    setAudioBlob(null);
                    setAudioUrl(null);
                    setTranscript("");
                    setDuration(0);
                    setState("idle");
                  }}
                  className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50"
                >
                  Record Again
                </button>
                <button
                  onClick={handleTranscribe}
                  disabled={state === "processing"}
                  className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg disabled:opacity-50"
                >
                  {state === "processing" ? "Transcribing..." : "Transcribe Audio"}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Transcript Display/Edit */}
        {(transcript || audioUrl) && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Appeal Story
            </label>
            <textarea
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Your transcribed text will appear here, or type your appeal story directly..."
              className="w-full h-48 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
            <p className="text-gray-500 text-sm mt-2">
              {transcript.length} characters
            </p>
          </div>
        )}

        {/* UPL Notice */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded mb-6">
          <p className="text-sm text-gray-700">
            <strong>Note:</strong> We will help format your story into a
            professional appeal letter, but we do not provide legal advice or
            recommend specific arguments.
          </p>
        </div>

        {/* Navigation */}
        <div className="flex gap-4">
          <Link
            href="/appeal/camera"
            className="flex-1 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium text-center hover:bg-gray-50 transition-colors"
          >
            ← Back
          </Link>
          <button
            onClick={handleContinue}
            disabled={!transcript.trim() && !audioUrl}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue → {transcript && `(${transcript.length} chars)`}
          </button>
        </div>
      </div>
    </div>
  );
}

