import requests
import json
import random
import string
import sys

BASE_URL = "http://localhost:3000"

def generate_repo_name():
    # Generate a random string for the repo name
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"test-prototype-{random_suffix}"

def test_search_prototypes():
    print("\n🔍 Searching for AI UI prototypes...")
    response = requests.get(f"{BASE_URL}/search-prototypes")
    data = response.json()
    
    if not data.get('data'):
        print("\n❌ No prototypes found")
        return None
        
    while True:
        print("\nFound AI prototypes:")
        for idx, repo in enumerate(data['data'], 1):
            print(f"\n{idx}. {'='*50}")
            print(f"📁 {repo['name']}")
            print(f"⭐ Stars: {repo['stars']}")
            print(f"🔄 Forks: {repo['forks_count']}")
            print(f"🔧 Language: {repo['language']}")
            print(f"📊 UI Files: {len(repo['ui_files'])}")
            print(f"🎮 Demo Available: {'Yes' if repo['has_demo'] else 'No'}")
            print(f"🏷️ Topics: {', '.join(repo['topics'])}")
            print(f"🔗 URL: {repo['url']}")
            print(f"📝 Description: {repo['description']}")
            print(f"\nUI Files Found:")
            for file in repo['ui_files'][:5]:
                print(f"  - {file}")
            if len(repo['ui_files']) > 5:
                print(f"  ... and {len(repo['ui_files']) - 5} more")
        
        print("\nOptions:")
        print("1-5: Choose a prototype to transform")
        print("r: Refresh search results")
        print("q: Quit")
        
        choice = input("\nEnter your choice: ").lower()
        
        if choice == 'q':
            print("\n👋 Goodbye!")
            sys.exit(0)
        elif choice == 'r':
            print("\n🔄 Refreshing search results...")
            response = requests.get(f"{BASE_URL}/search-prototypes")
            data = response.json()
            continue
        elif choice.isdigit() and 1 <= int(choice) <= len(data['data']):
            selected_repo = data['data'][int(choice) - 1]
            print(f"\n✅ Selected: {selected_repo['name']}")
            return selected_repo['url']
        else:
            print("\n❌ Invalid choice, please try again")

def test_create_from_prototype(source_repo_url: str):
    new_repo_name = generate_repo_name()
    data = {
        "source_repo_url": source_repo_url,
        "new_repo_name": new_repo_name
    }
    print(f"\n🚀 Creating new repository: {new_repo_name}")
    print(f"📋 Using prototype: {source_repo_url}")
    
    response = requests.post(
        f"{BASE_URL}/create-from-prototype",
        json=data
    )
    result = response.json()
    
    print("\n🎉 Repository created!")
    print(f"📁 Name: {new_repo_name}")
    print(f"🔗 URL: {result.get('repo_url')}")
    print(f"✨ Status: {result.get('message')}")
    
    return result.get("repo_url")

if __name__ == "__main__":
    print("Testing API endpoints...")
    
    # Search and select prototype
    while True:
        source_repo_url = test_search_prototypes()
        if source_repo_url:
            # Create new repository from the selected prototype
            new_repo_url = test_create_from_prototype(source_repo_url)
            print(f"\nNew repository created at: {new_repo_url}")
            
            print("\nOptions:")
            print("1: Transform another prototype")
            print("q: Quit")
            
            choice = input("\nEnter your choice: ").lower()
            if choice == 'q':
                print("\n👋 Goodbye!")
                break
            elif choice == '1':
                continue
            else:
                print("\n❌ Invalid choice, quitting...")
                break
        else:
            print("\n❌ No prototype repositories found to clone from")
            break 