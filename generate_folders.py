import os
import time
from github import Github, GithubException, Auth

# ==========================================
# ⚙️ CONFIGURATION SETTINGS
# ==========================================
GITHUB_TOKEN = os.getenv("GH_TOKEN") 
REPO_NAME = "Automation8248/Faceless-fact-yt"

# ==========================================
# 📊 HARDCODED DATA (Categories & Topics)
# ==========================================
# Is list mein aap apne naye topics bhi directly add kar sakte hain.
DATA = [
    {'Topic': 'Animals', 'Category': 'Cats'}, {'Topic': 'Animals', 'Category': 'Dogs'}, {'Topic': 'Animals', 'Category': 'Elephants'}, {'Topic': 'Animals', 'Category': 'Lions'}, {'Topic': 'Animals', 'Category': 'Tigers'},
    {'Topic': 'Animals', 'Category': 'Bears'}, {'Topic': 'Animals', 'Category': 'Wolves'}, {'Topic': 'Animals', 'Category': 'Foxes'}, {'Topic': 'Animals', 'Category': 'Monkeys'}, {'Topic': 'Animals', 'Category': 'Gorillas'},
    {'Topic': 'Animals', 'Category': 'Chimpanzees'}, {'Topic': 'Animals', 'Category': 'Giraffes'}, {'Topic': 'Animals', 'Category': 'Zebras'}, {'Topic': 'Animals', 'Category': 'Horses'}, {'Topic': 'Animals', 'Category': 'Pandas'},
    {'Topic': 'Animals', 'Category': 'Koalas'}, {'Topic': 'Animals', 'Category': 'Kangaroos'}, {'Topic': 'Animals', 'Category': 'Dolphins'}, {'Topic': 'Animals', 'Category': 'Whales'}, {'Topic': 'Animals', 'Category': 'Sharks'},
    {'Topic': 'Human Body', 'Category': 'Heart'}, {'Topic': 'Human Body', 'Category': 'Brain'}, {'Topic': 'Human Body', 'Category': 'Lungs'}, {'Topic': 'Human Body', 'Category': 'Liver'}, {'Topic': 'Human Body', 'Category': 'Kidneys'},
    {'Topic': 'Human Brain', 'Category': 'Memory'}, {'Topic': 'Human Brain', 'Category': 'Dreams'}, {'Topic': 'Human Brain', 'Category': 'Consciousness'}, {'Topic': 'Human Brain', 'Category': 'Neurons'}, {'Topic': 'Human Brain', 'Category': 'Emotions'},
    {'Topic': 'Psychology', 'Category': 'Behavior'}, {'Topic': 'Psychology', 'Category': 'Memory'}, {'Topic': 'Psychology', 'Category': 'Emotions'}, {'Topic': 'Psychology', 'Category': 'Fear'}, {'Topic': 'Psychology', 'Category': 'Love'},
    {'Topic': 'Ocean', 'Category': 'Waves'}, {'Topic': 'Ocean', 'Category': 'Tides'}, {'Topic': 'Ocean', 'Category': 'Currents'}, {'Topic': 'Ocean', 'Category': 'Coral Reefs'}, {'Topic': 'Ocean', 'Category': 'Marine Life'},
    {'Topic': 'Deep Sea', 'Category': 'Abyssal Zone'}, {'Topic': 'Deep Sea', 'Category': 'Hadal Zone'}, {'Topic': 'Deep Sea', 'Category': 'Trenches'}, {'Topic': 'Deep Sea', 'Category': 'Deep Sea Fish'}, {'Topic': 'Deep Sea', 'Category': 'Anglerfish'},
    {'Topic': 'Space', 'Category': 'Solar System'}, {'Topic': 'Space', 'Category': 'Planets'}, {'Topic': 'Space', 'Category': 'Moons'}, {'Topic': 'Space', 'Category': 'Asteroids'}, {'Topic': 'Space', 'Category': 'Comets'},
    {'Topic': 'Universe', 'Category': 'Big Bang'}, {'Topic': 'Universe', 'Category': 'Cosmology'}, {'Topic': 'Universe', 'Category': 'Galaxies'}, {'Topic': 'Universe', 'Category': 'Stars'}, {'Topic': 'Universe', 'Category': 'Nebulae'},
    {'Topic': 'Black Holes', 'Category': 'Event Horizon'}, {'Topic': 'Black Holes', 'Category': 'Singularity'}, {'Topic': 'Black Holes', 'Category': 'Accretion Disk'}, {'Topic': 'Black Holes', 'Category': 'Black Hole Mergers'}, {'Topic': 'Black Holes', 'Category': 'Stellar Black Holes'},
    {'Topic': 'Alien Life', 'Category': 'Exoplanets'}, {'Topic': 'Alien Life', 'Category': 'Habitable Zones'}, {'Topic': 'Alien Life', 'Category': 'Water Worlds'}, {'Topic': 'Alien Life', 'Category': 'Extremophiles'}, {'Topic': 'Alien Life', 'Category': 'Mars Life'},
    {'Topic': 'Dinosaurs', 'Category': 'Tyrannosaurus'}, {'Topic': 'Dinosaurs', 'Category': 'Triceratops'}, {'Topic': 'Dinosaurs', 'Category': 'Velociraptor'}, {'Topic': 'Dinosaurs', 'Category': 'Brachiosaurus'}, {'Topic': 'Dinosaurs', 'Category': 'Stegosaurus'},
    {'Topic': 'Ancient Mysteries', 'Category': 'Pyramids'}, {'Topic': 'Ancient Mysteries', 'Category': 'Stonehenge'}, {'Topic': 'Ancient Mysteries', 'Category': 'Nazca Lines'}, {'Topic': 'Ancient Mysteries', 'Category': 'Antikythera Mechanism'}, {'Topic': 'Ancient Mysteries', 'Category': 'Terracotta Army'},
    {'Topic': 'Unsolved Mysteries', 'Category': 'Missing Persons'}, {'Topic': 'Unsolved Mysteries', 'Category': 'Unidentified Bodies'}, {'Topic': 'Unsolved Mysteries', 'Category': 'Unsolved Crimes'}, {'Topic': 'Unsolved Mysteries', 'Category': 'Mysterious Disappearances'},
    {'Topic': 'Science Mysteries', 'Category': 'Dark Matter'}, {'Topic': 'Science Mysteries', 'Category': 'Dark Energy'}, {'Topic': 'Science Mysteries', 'Category': 'Quantum Mechanics'}, {'Topic': 'Science Mysteries', 'Category': 'Consciousness'},
    {'Topic': 'Human Survival', 'Category': 'Extreme Cold'}, {'Topic': 'Human Survival', 'Category': 'Extreme Heat'}, {'Topic': 'Human Survival', 'Category': 'Dehydration'}, {'Topic': 'Human Survival', 'Category': 'Starvation'},
    {'Topic': 'Dangerous Animals', 'Category': 'Sharks'}, {'Topic': 'Dangerous Animals', 'Category': 'Crocodiles'}, {'Topic': 'Dangerous Animals', 'Category': 'Snakes'}, {'Topic': 'Dangerous Animals', 'Category': 'Lions'}, {'Topic': 'Dangerous Animals', 'Category': 'Tigers'},
    {'Topic': 'Extreme Places', 'Category': 'Mariana Trench'}, {'Topic': 'Extreme Places', 'Category': 'Mount Everest'}, {'Topic': 'Extreme Places', 'Category': 'Death Valley'}, {'Topic': 'Extreme Places', 'Category': 'Atacama Desert'},
    {'Topic': 'Strange Discoveries', 'Category': 'Ancient Artifacts'}, {'Topic': 'Strange Discoveries', 'Category': 'Fossils'}, {'Topic': 'Strange Discoveries', 'Category': 'Unusual Animals'}, {'Topic': 'Strange Discoveries', 'Category': 'Rare Minerals'},
    {'Topic': 'Ancient Civilizations', 'Category': 'Egypt'}, {'Topic': 'Ancient Civilizations', 'Category': 'Rome'}, {'Topic': 'Ancient Civilizations', 'Category': 'Greece'}, {'Topic': 'Ancient Civilizations', 'Category': 'Maya'},
    {'Topic': 'Lost Civilizations', 'Category': 'Atlantis'}, {'Topic': 'Lost Civilizations', 'Category': 'Maya Cities'}, {'Topic': 'Lost Civilizations', 'Category': 'Harappa'}, {'Topic': 'Lost Civilizations', 'Category': 'Mohenjo Daro'},
    {'Topic': 'Future Technology', 'Category': 'Artificial Intelligence'}, {'Topic': 'Future Technology', 'Category': 'Robotics'}, {'Topic': 'Future Technology', 'Category': 'Quantum Computers'}, {'Topic': 'Future Technology', 'Category': 'Brain Computer Interfaces'},
    {'Topic': 'Time Travel', 'Category': 'Time Dilation'}, {'Topic': 'Time Travel', 'Category': 'Relativity'}, {'Topic': 'Time Travel', 'Category': 'Wormholes'}, {'Topic': 'Time Travel', 'Category': 'Closed Timelike Curves'},
    {'Topic': 'Parallel Universe', 'Category': 'Multiverse'}, {'Topic': 'Parallel Universe', 'Category': 'Many Worlds'}, {'Topic': 'Parallel Universe', 'Category': 'Bubble Universes'}, {'Topic': 'Parallel Universe', 'Category': 'Brane Worlds'},
    {'Topic': 'Weird Science', 'Category': 'Strange Materials'}, {'Topic': 'Weird Science', 'Category': 'Liquid Metal'}, {'Topic': 'Weird Science', 'Category': 'Non Newtonian Fluids'}, {'Topic': 'Weird Science', 'Category': 'Quantum Effects'},
    {'Topic': 'Natural Phenomena', 'Category': 'Auroras'}, {'Topic': 'Natural Phenomena', 'Category': 'Lightning'}, {'Topic': 'Natural Phenomena', 'Category': 'Thunder'}, {'Topic': 'Natural Phenomena', 'Category': 'Tornadoes'},
    {'Topic': 'World Records', 'Category': 'Tallest Person'}, {'Topic': 'World Records', 'Category': 'Shortest Person'}, {'Topic': 'World Records', 'Category': 'Fastest Animal'}, {'Topic': 'World Records', 'Category': 'Fastest Human'}
    # Aap zaroorat ke hisaab se is list me comma lagakar aur items add kar sakte hain
]

def aggressive_create_file(repo, path, message, content):
    """File create karne ka aggressive function jo errors handle karega"""
    try:
        repo.create_file(path=path, message=message, content=content, branch="main")
        return True, "✅ Created"
    except GithubException as e:
        if e.status == 422:
            return False, "⏭️ Skipped (Already exists)"
        elif e.status == 403:
            # Agar GitHub api limit touch kare toh 2 second ruk kar wapas try kare
            time.sleep(2)
            try:
                repo.create_file(path=path, message=message, content=content, branch="main")
                return True, "✅ Created on Retry"
            except:
                return False, f"❌ Failed on Retry: {e.data.get('message', str(e))}"
        else:
            return False, f"❌ Error: {e.data.get('message', str(e))}"

def create_github_files():
    print("🚀 Starting ULTRA-FAST Folder Generation...")
    
    if not GITHUB_TOKEN:
        print("❌ Error: GH_TOKEN secret is not set!")
        return

    try:
        # Naya Token Auth Format
        auth = Auth.Token(GITHUB_TOKEN)
        g = Github(auth=auth)
        repo = g.get_repo(REPO_NAME)
        print(f"✅ Connected to repository: {REPO_NAME}")
    except Exception as e:
        print(f"❌ GitHub connection failed: {e}")
        return

    print(f"✅ Loaded {len(DATA)} topics directly from code. No Excel required!\n")
    print("-" * 50)
    
    # ⚡ Super fast loop direct list se chalega
    for index, row in enumerate(DATA):
        main_topic = str(row['Topic']).strip()      
        sub_category = str(row['Category']).strip() 
        
        facts_path = f"Topics/{main_topic}/{sub_category}/facts.txt"
        images_path = f"Topics/{main_topic}/{sub_category}/images/1.txt"
        
        print(f"⚡ [{index + 1}/{len(DATA)}] {main_topic} -> {sub_category}")
        
        # Create facts.txt quickly
        status1, msg1 = aggressive_create_file(
            repo, facts_path, 
            f"Auto: Facts for {sub_category}", 
            f"Here are amazing facts about {sub_category}."
        )
        print(f"  ├── {msg1}: {facts_path}")

        # Create images/1.txt quickly
        status2, msg2 = aggressive_create_file(
            repo, images_path, 
            f"Auto: Image for {sub_category}", 
            f"Image URL for {sub_category} will be saved here."
        )
        print(f"  └── {msg2}: {images_path}")
            
    print("-" * 50)
    print("🎉 ALL DONE! Maximum speed execution finished.")

if __name__ == "__main__":
    create_github_files()
