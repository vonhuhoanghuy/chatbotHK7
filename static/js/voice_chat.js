class VoiceChat {
    constructor() {
        console.log('Initializing VoiceChat...');
        
        if (!('webkitSpeechRecognition' in window)) {
            console.error('Speech Recognition không được hỗ trợ');
            alert('Trình duyệt của bạn không hỗ trợ nhận dạng giọng nói');
            return;
        }

        this.recognition = new webkitSpeechRecognition();
        this.setupRecognition();
        this.setupUI();
    }

    setupRecognition() {
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'vi-VN';
        this.recognition.maxAlternatives = 1;
        this.recordingTimeout = null;

        var self = this;

        this.recognition.onstart = function() {
            console.log('Bắt đầu ghi âm...');
            self.updateUI(true);
            
            self.recordingTimeout = setTimeout(function() {
                console.log('Timeout - không phát hiện giọng nói');
                self.stopRecording();
            }, 5000);
        };

        this.recognition.onend = function() {
            console.log('Kết thúc ghi âm');
            self.updateUI(false);
            if (self.recordingTimeout) {
                clearTimeout(self.recordingTimeout);
            }
        };

        this.recognition.onresult = function(event) {
            if (self.recordingTimeout) {
                clearTimeout(self.recordingTimeout);
            }

            var last = event.results.length - 1;
            var text = event.results[last][0].transcript;
            
            console.log('Văn bản nhận dạng được:', text);
            
            if (text.trim()) {
                document.getElementById('user-input').value = text;
                if (event.results[last].isFinal) {
                    document.getElementById('send-button').click();
                }
            }
        };

        this.recognition.onerror = function(event) {
            console.log('Lỗi Speech Recognition:', event.error);
            
            switch (event.error) {
                case 'no-speech':
                    self.statusSpan.textContent = 'Không phát hiện giọng nói, vui lòng thử lại';
                    break;
                case 'audio-capture':
                    self.statusSpan.textContent = 'Không tìm thấy microphone';
                    break;
                case 'not-allowed':
                    self.statusSpan.textContent = 'Vui lòng cho phép truy cập microphone';
                    break;
                default:
                    self.statusSpan.textContent = 'Có lỗi xảy ra, vui lòng thử lại';
            }

            setTimeout(function() {
                self.statusSpan.textContent = '';
            }, 3000);
            self.updateUI(false);
        };

        this.recognition.onsoundstart = function() {
            console.log('Đã phát hiện âm thanh');
            self.statusSpan.textContent = 'Đang nghe...';
            if (self.recordingTimeout) {
                clearTimeout(self.recordingTimeout);
            }
        };

        this.recognition.onsoundend = function() {
            console.log('Kết thúc âm thanh');
            self.statusSpan.textContent = 'Đã nghe xong, đang xử lý...';
        };
    }

    setupUI() {
        this.startButton = document.getElementById('start-recording');
        this.stopButton = document.getElementById('stop-recording');
        this.statusSpan = document.getElementById('recording-status');

        var self = this;

        this.startButton.addEventListener('click', function() {
            self.startRecording();
        });

        this.stopButton.addEventListener('click', function() {
            self.stopRecording();
        });
    }

    startRecording() {
        try {
            this.recognition.start();
            this.statusSpan.textContent = 'Hãy nói gì đó...';
        } catch (error) {
            console.error('Lỗi khi bắt đầu ghi âm:', error);
            this.statusSpan.textContent = 'Không thể bắt đầu ghi âm';
        }
    }

    stopRecording() {
        try {
            this.recognition.stop();
            this.statusSpan.textContent = '';
        } catch (error) {
            console.error('Lỗi khi dừng ghi âm:', error);
        }
    }

    updateUI(isRecording) {
        this.startButton.style.display = isRecording ? 'none' : 'flex';
        this.stopButton.style.display = isRecording ? 'flex' : 'none';
        
        if (isRecording) {
            this.stopButton.classList.add('recording');
        } else {
            this.stopButton.classList.remove('recording');
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    new VoiceChat();
}); 