import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import asyncio
import tempfile
import edge_tts

async def play_voice(text, voice):
    print(f"Playing {voice}...")
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, f"{voice}.mp3")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(temp_file)
    
    pygame.mixer.init()
    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)
    pygame.mixer.music.unload()
    pygame.mixer.quit()
    try: 
        os.remove(temp_file)
    except: 
        pass

async def main():
    print("🔊 Testing Male Hindi Voice (`hi-IN-MadhurNeural`)")
    await play_voice("नमस्ते! मैं मधुर हूँ, यह एक प्राकृतिक हिंदी पुरुष की आवाज़ है।", "hi-IN-MadhurNeural")
    
    await asyncio.sleep(1)
    
    print("🔊 Testing Male Indian English Voice (`en-IN-PrabhatNeural`)")
    await play_voice("Hello boss, I am Prabhat, an Indian English male voice.", "en-IN-PrabhatNeural")
    
    await asyncio.sleep(1)
    
    print("🔊 Testing Female Indian English Voice (`en-IN-NeerjaNeural`)")
    await play_voice("And hello again, I am Neerja, the Indian English female voice.", "en-IN-NeerjaNeural")
    
    print("\n✅ All voice tests complete!")

if __name__ == "__main__":
    asyncio.run(main())
