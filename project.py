# Required dependencies:
# pip install gtts pygame customtkinter pillow sounddevice numpy scipy pydub
import customtkinter as ctk
from gtts import gTTS
import pygame
import os
import sounddevice as sd
import soundfile as sf
from tkinter import filedialog
from threading import Thread
import numpy as np
from scipy import signal
import tempfile
import re
from pydub import AudioSegment
from pydub.effects import speedup

class MarathiDialect:
    def __init__(self, name, substitutions, rhythm_pattern=1.0, articulation=1.0, style='neutral'):
        self.name = name
        self.substitutions = substitutions
        self.rhythm_pattern = rhythm_pattern
        self.articulation = articulation
        self.style = style

    def apply_dialect(self, text):
        """Apply dialect-specific substitutions to text"""
        modified_text = text
        for original, replacement in self.substitutions.items():
            modified_text = modified_text.replace(original, replacement)
        return modified_text

class EmotionModifier:
    def __init__(self):
        # Emotion parameters with built-in speed and volume adjustments
        self.emotions = {
            'neutral': {'intensity': 1.0, 'speed_factor': 1.0, 'volume': 0.9, 'pause_length': 1.0},
            'happy': {'intensity': 1.15, 'speed_factor': 1.1, 'volume': 1.1, 'pause_length': 0.8},
            'angry': {'intensity': 1.8, 'speed_factor': -1.13, 'volume': 1.8, 'pause_length': 0.25},
            'sad': {'intensity': 0.8, 'speed_factor': 0.89, 'volume': 0.7, 'pause_length': 1.4},
            'punctuation': {'intensity': 1.0, 'speed_factor': 1.2, 'volume': 1.7, 'pause_length': 1.0}
        }

    def modify_audio(self, audio_data, emotion='neutral'):
        params = self.emotions[emotion]
        modified = audio_data.copy()
        
        # Apply intensity
        if params['intensity'] != 1.0:
            modified = self.change_intensity(modified, params['intensity'])
            
        # Handle speed factor (convert negative to appropriate positive value)
        speed_factor = params['speed_factor']
        if speed_factor != 1.0:
            actual_speed = abs(speed_factor) if speed_factor > 0 else (1 / abs(speed_factor))
            modified = self.change_rhythm(modified, actual_speed)
            
        # Apply volume
        modified = modified * params['volume']
        return modified

    def change_intensity(self, audio_data, intensity_factor):
        """Change articulation intensity without affecting base tone"""
        mean_val = np.mean(audio_data)
        modified = mean_val + (audio_data - mean_val) * intensity_factor
        return modified

    def change_rhythm(self, audio_data, rhythm_factor):
        """Change speech rhythm/speed without affecting tone"""
        if rhythm_factor <= 0:
            rhythm_factor = 1.0
        return signal.resample(audio_data, int(len(audio_data) / rhythm_factor))

class MarathiTTS:
    def __init__(self):
        pygame.mixer.init()
        self.emotion_modifier = EmotionModifier()
        
        # Dialect definitions
        self.dialects = {
            'standard': MarathiDialect('मानक मराठी', {}, 1.0, 1.0),
            'varhadi': MarathiDialect('वरहाडी', {
                'गा': 'मा', 'ळ': 'ल', 'आहे': 'आय', 'नाही': 'नाय',
                'काय': 'काय', 'मी': 'म्ही', 'तू': 'तु',
                'आपण': 'आपुण', 'झाला': 'झाला',
                'पाहिजे': 'पाहिजे', 'बोलतो': 'बोलतो'
            }, 1.1, 1.15),
            'ahirani': MarathiDialect('अहिराणी', {
                'आहे': 'हाय', 'नाही': 'नाय', 'मला': 'म्हाला',
                'तुला': 'तुला', 'झाला': 'झालं',
                'काय': 'काय', 'कसं': 'कसं',
                'पाहिजे': 'पायजे', 'जातो': 'जातो'
            }, 1.12, 1.2),
            'malwani': MarathiDialect('मालवणी', {
                'व': 'व्ह', 'च': 'च', 'झ': 'झ', 'आहे': 'आस',
                'नाही': 'नाय', 'काय': 'काय',
                'कसं': 'कसं', 'तुला': 'तुज्जा',
                'मला': 'मज्जा', 'पाहिजे': 'पायजे'
            }, 0.92, 0.9),
            'nagpuri': MarathiDialect('नागपुरी', {
                'आहे': 'हाय', 'नाही': 'नाय', 'मला': 'म्हाला',
                'तुला': 'तुला', 'आपण': 'आपुण',
                'काय': 'काय', 'करतो': 'करतो',
                'बोलतो': 'बोलतो'
            }, 1.12, 1.2),
            'konkani': MarathiDialect('कोकणी', {
                'आहे': 'आसा', 'नाही': 'ना', 'काय': 'कितं',
                'कसं': 'कसं', 'तुला': 'तुका',
                'मला': 'माका', 'पाहिजे': 'जाय'
            }, 0.95, 0.93)
        }
        self.temp_file = None
        self.current_audio_data = None
        self.current_sample_rate = None
        self.is_playing = False
        self.sample_rate = 22050

    def generate_speech(self, text, dialect='standard', emotion='neutral', save_path=None):
        try:
            if emotion == 'punctuation':
                return self.generate_punctuated_speech(text, dialect, save_path)
            else:
                return self.generate_basic_speech(text, dialect, emotion, save_path)
        except Exception as e:
            print(f"Error generating speech: {str(e)}")
            return None

    def generate_basic_speech(self, text, dialect='standard', emotion='neutral', save_path=None):
        """Generate speech without punctuation-based modulation"""
        try:
            modified_text = self.dialects[dialect].apply_dialect(text)
            temp = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_path = temp.name
            temp.close()
            
            tts = gTTS(text=modified_text, lang='mr', slow=False)
            mp3_path = temp_path.replace('.wav', '.mp3')
            tts.save(mp3_path)
            
            audio_data, sample_rate = sf.read(mp3_path)
            self.current_sample_rate = sample_rate
            
            dialect_obj = self.dialects[dialect]
            audio_data = self.emotion_modifier.change_rhythm(audio_data, dialect_obj.rhythm_pattern)
            modified_audio = np.mean(audio_data) + (audio_data - np.mean(audio_data)) * dialect_obj.articulation
            modified_audio = self.emotion_modifier.modify_audio(modified_audio, emotion)
            
            self.current_audio_data = modified_audio
            sf.write(temp_path, modified_audio, sample_rate)
            
            os.unlink(mp3_path)
            self.temp_file = temp_path
            
            if save_path:
                sf.write(save_path, modified_audio, sample_rate)
            return temp_path
            
        except Exception as e:
            print(f"Error generating basic speech: {str(e)}")
            return None

    def generate_punctuated_speech(self, text, dialect='standard', save_path=None):
        """Generate speech with punctuation-based modulation"""
        try:
            # Parameters for punctuation modulation
            question_volume_increase_db = 10.0
            exclamation_speed_factor = 1.3
            other_volume_decrease_db = 5.0
            
            # Find sentences using punctuation
            pattern = r'[^।?!.,;:"\']+[।?!.,;:"\']+|\s*$'
            sentences = re.findall(pattern, text)
            
            if not sentences:
                sentences = [text]  # If no punctuation, treat as one sentence
                
            # Apply dialect modifications to all text
            dialect_obj = self.dialects[dialect]
            
            # Create temp files
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_wav_path = temp_wav.name
            temp_wav.close()
            
            temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_mp3_path = temp_mp3.name
            temp_mp3.close()
            
            # Process each sentence separately
            full_audio = None
            
            for sentence in sentences:
                if not sentence.strip():
                    continue
                    
                # Apply dialect to the sentence
                modified_sentence = dialect_obj.apply_dialect(sentence)
                
                # Generate speech for the sentence
                sentence_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                sentence_mp3_path = sentence_mp3.name
                sentence_mp3.close()
                
                tts = gTTS(text=modified_sentence, lang='mr')
                tts.save(sentence_mp3_path)
                
                # Process with pydub
                audio = AudioSegment.from_mp3(sentence_mp3_path)
                
                # Apply punctuation-based modifications
                last_char = sentence.strip()[-1] if sentence.strip() else ''
                
                if last_char == '?':
                    # Increase volume for questions
                    audio = audio + question_volume_increase_db
                elif last_char == '!':
                    # Speed up for exclamations
                    audio = speedup(audio, playback_speed=exclamation_speed_factor, chunk_size=150, crossfade=25)
                else:
                    # Slight volume reduction for regular sentences
                    audio = audio - other_volume_decrease_db
                
                # Add to full audio
                if full_audio is None:
                    full_audio = audio
                else:
                    full_audio += audio
                    
                # Clean up temp file
                os.unlink(sentence_mp3_path)
            
            if full_audio:
                # Export the final audio
                full_audio.export(temp_mp3_path, format="mp3")
                
                # Convert to numpy array for consistency with the rest of the system
                audio_data, sample_rate = sf.read(temp_mp3_path)
                self.current_sample_rate = sample_rate
                self.current_audio_data = audio_data
                
                # Apply dialect's rhythm pattern and articulation
                audio_data = self.emotion_modifier.change_rhythm(audio_data, dialect_obj.rhythm_pattern)
                modified_audio = np.mean(audio_data) + (audio_data - np.mean(audio_data)) * dialect_obj.articulation
                
                # Save the audio
                sf.write(temp_wav_path, modified_audio, sample_rate)
                self.temp_file = temp_wav_path
                
                if save_path:
                    sf.write(save_path, modified_audio, sample_rate)
                    
                # Clean up the temp MP3
                os.unlink(temp_mp3_path)
                
                return temp_wav_path
            else:
                raise Exception("No audio was generated")
                
        except Exception as e:
            print(f"Error generating punctuated speech: {str(e)}")
            if 'temp_mp3_path' in locals() and os.path.exists(temp_mp3_path):
                os.unlink(temp_mp3_path)
            if 'temp_wav_path' in locals() and os.path.exists(temp_wav_path):
                os.unlink(temp_wav_path)
            return None

    def play(self):
        if self.temp_file and not self.is_playing:
            pygame.mixer.music.load(self.temp_file)
            pygame.mixer.music.play()
            self.is_playing = True
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            self.is_playing = False

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def save(self, path):
        if self.current_audio_data is not None and self.current_sample_rate:
            sf.write(path, self.current_audio_data, self.current_sample_rate)
            return True
        return False

    def cleanup(self):
        if self.temp_file and os.path.exists(self.temp_file):
            os.unlink(self.temp_file)

class TTSUI:
    def __init__(self):
        self.tts_engine = MarathiTTS()
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.window = ctk.CTk()
        self.window.title("मराठी टेक्स्ट-टू-स्पीच")
        self.window.geometry("800x700")
        
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="स्मार्ट स्पीच मॉडिफिकेशन फॉर प्रोसोडी कन्व्हर्जन इन एक्स्प्रेसिव्ह मराठी टेक्स्ट टू स्पीच सिंथेसिस",
            font=("Noto Sans Devanagari", 24, "bold")
        )
        self.title_label.pack(pady=10)
        
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(pady=10, padx=20, fill="x")
        
        self.input_label = ctk.CTkLabel(
            self.input_frame,
            text="मजकूर टाका:",
            font=("Noto Sans Devanagari", 16)
        )
        self.input_label.pack(pady=5)
        
        self.text_input = ctk.CTkTextbox(
            self.input_frame,
            height=200,
            font=("Noto Sans Devanagari", 14)
        )
        self.text_input.pack(pady=5, fill="x")
        
        self.controls_frame = ctk.CTkFrame(self.main_frame)
        self.controls_frame.pack(pady=10, padx=20, fill="x")
        
        self.dialect_label = ctk.CTkLabel(
            self.controls_frame,
            text="बोली निवडा:",
            font=("Noto Sans Devanagari", 12)
        )
        self.dialect_label.pack(pady=5)
        
        self.dialect_var = ctk.StringVar(value="standard")
        self.dialect_menu = ctk.CTkOptionMenu(
            self.controls_frame,
            values=list(self.tts_engine.dialects.keys()),
            variable=self.dialect_var,
            font=("Noto Sans Devanagari", 12)
        )
        self.dialect_menu.pack(pady=5)
        
        self.emotion_label = ctk.CTkLabel(
            self.controls_frame,
            text="भावना निवडा:",
            font=("Noto Sans Devanagari", 12)
        )
        self.emotion_label.pack(pady=5)
        
        self.emotion_var = ctk.StringVar(value="neutral")
        self.emotion_menu = ctk.CTkOptionMenu(
            self.controls_frame,
            values=list(self.tts_engine.emotion_modifier.emotions.keys()),
            variable=self.emotion_var,
            font=("Noto Sans Devanagari", 12),
            command=self.update_emotion_info
        )
        self.emotion_menu.pack(pady=5)
        
        self.emotion_characteristics = {
            'neutral': "न्यूट्रल - सामान्य वेग आणि आवाज",
            'happy': "आनंदी - थोडा जास्त वेग आणि जास्त आवाज",
            'angry': "रागीट - थोडा कमी वेग आणि जास्त आवाज",
            'sad': "दुःखी - कमी वेग आणि कमी आवाज",
            'punctuation': "विरामचिन्हे - प्रश्नचिन्हांसाठी जास्त आवाज, उद्गारचिन्हांसाठी जास्त वेग"
        }
        self.emotion_info_label = ctk.CTkLabel(
            self.controls_frame,
            text=self.emotion_characteristics['neutral'],
            font=("Noto Sans Devanagari", 12)
        )
        self.emotion_info_label.pack(pady=5)
        
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=10, padx=20, fill="x")
        
        self.play_button = ctk.CTkButton(
            self.button_frame,
            text="बोलणे सुरू करा",
            command=self.play_speech,
            font=("Noto Sans Devanagari", 14),
            height=40
        )
        self.play_button.pack(side="left", padx=10, expand=True)
        
        self.stop_button = ctk.CTkButton(
            self.button_frame,
            text="थांबवा",
            command=self.stop_speech,
            font=("Noto Sans Devanagari", 14),
            height=40
        )
        self.stop_button.pack(side="left", padx=10, expand=True)
        
        self.save_button = ctk.CTkButton(
            self.button_frame,
            text="ऑडिओ सेव्ह करा",
            command=self.save_audio,
            font=("Noto Sans Devanagari", 14),
            height=40
        )
        self.save_button.pack(side="left", padx=10, expand=True)
        
        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="मजकूर साफ करा",
            command=self.clear_text,
            font=("Noto Sans Devanagari", 14),
            height=40
        )
        self.clear_button.pack(side="right", padx=10, expand=True)
        
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Noto Sans Devanagari", 12)
        )
        self.status_label.pack(pady=10)
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_emotion_info(self, emotion):
        self.emotion_info_label.configure(text=self.emotion_characteristics[emotion])

    def play_speech(self):
        self.status_label.configure(text="बोलणे तयार होत आहे...")
        self.window.update()
        text = self.text_input.get("1.0", "end-1c")
        if not text.strip():
            self.status_label.configure(text="कृपया मजकूर टाका!")
            return
        dialect = self.dialect_var.get()
        emotion = self.emotion_var.get()
        
        def generate_and_play():
            try:
                audio_file = self.tts_engine.generate_speech(text, dialect, emotion)
                if audio_file:
                    self.tts_engine.play()
                    
                    # Get appropriate status message based on emotion
                    if emotion == 'punctuation':
                        status_text = "बोलणे सुरू आहे... (विरामचिन्हे प्रभाव सह)"
                    else:
                        emotion_params = self.tts_engine.emotion_modifier.emotions[emotion]
                        speed_factor = emotion_params['speed_factor']
                        volume_factor = emotion_params['volume']
                        emotion_name_map = {
                            'neutral': 'न्यूट्रल',
                            'happy': 'आनंदी',
                            'angry': 'रागीट',
                            'sad': 'दुःखी',
                            'punctuation': 'विरामचिन्हे'
                        }
                        emotion_name = emotion_name_map.get(emotion, emotion)
                        status_text = f"बोलणे सुरू आहे... ({emotion_name} भावना: वेग {speed_factor:.1f}x, आवाज {volume_factor:.1f}x)"
                    
                    self.status_label.configure(text=status_text)
                else:
                    self.status_label.configure(text="बोलणे तयार करताना त्रुटी आली.")
            except Exception as e:
                self.status_label.configure(text=f"त्रुटी: {str(e)}")
                
        Thread(target=generate_and_play, daemon=True).start()

    def save_audio(self):
        if self.tts_engine.current_audio_data is None:
            self.status_label.configure(text="आधी बोलणे तयार करा!")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV Audio", "*.wav"), ("All files", "*.*")],
            title="ऑडिओ फाइल सेव्ह करा"
        )
        if file_path:
            if self.tts_engine.save(file_path):
                self.status_label.configure(text=f"ऑडिओ सेव्ह केला: {os.path.basename(file_path)}")
            else:
                self.status_label.configure(text="ऑडिओ सेव्ह करताना त्रुटी आली")

    def stop_speech(self):
        self.tts_engine.stop()
        self.status_label.configure(text="बोलणे थांबवले")

    def clear_text(self):
        self.text_input.delete("1.0", "end")
        self.status_label.configure(text="")

    def on_closing(self):
        self.tts_engine.cleanup()
        self.window.destroy()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = TTSUI()
    app.run()