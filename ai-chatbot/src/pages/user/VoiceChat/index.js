export default class VoiceChat {
  constructor(onVoiceInput, statusSpan) {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.error(
        "Speech Recognition không được hỗ trợ trên trình duyệt này."
      );
      alert(
        "Trình duyệt của bạn không hỗ trợ nhận dạng giọng nói. Hãy sử dụng Google Chrome."
      );
      return;
    }

    this.recognition = new SpeechRecognition();
    this.statusSpan = statusSpan;
    this.onVoiceInput = onVoiceInput;
    this.setupRecognition();
  }

  setupRecognition() {
    this.recognition.lang = "vi-VN";
    this.recognition.continuous = false;
    this.recognition.interimResults = true;

    this.recognition.onstart = () => {
      console.log("Bắt đầu ghi âm...");
      this.statusSpan.textContent = "Hãy nói gì đó...";
    };

    this.recognition.onresult = (event) => {
      const last = event.results.length - 1;
      const text = event.results[last][0].transcript.trim();

      if (event.results[last].isFinal) {
        console.log("Văn bản cuối cùng:", text);
        if (text) this.onVoiceInput(text);
      } else {
        console.log("Văn bản tạm thời:", text);
      }
    };

    this.recognition.onerror = (event) => {
      console.error("Lỗi nhận dạng giọng nói:", event.error);
      this.statusSpan.textContent = "Có lỗi xảy ra, vui lòng thử lại.";
    };

    this.recognition.onend = () => {
      console.log("Kết thúc ghi âm");
      this.statusSpan.textContent = "";
    };
  }

  startRecording() {
    try {
      this.recognition.start();
    } catch (error) {
      console.error("Lỗi khi bắt đầu ghi âm:", error);
      this.statusSpan.textContent = "Không thể bắt đầu ghi âm.";
    }
  }

  stopRecording() {
    try {
      this.recognition.stop();
    } catch (error) {
      console.error("Lỗi khi dừng ghi âm:", error);
    }
  }
}
