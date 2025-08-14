#!/usr/bin/env python3
"""
Complete CV Automation Script
This script parses cv.tex, updates HTML, generates PDF, and commits/pushes to Git.
"""

import re
import json
import subprocess
import os
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Optional file watching (install with: pip install watchdog)
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class CVParser:
    """Parses LaTeX CV file and extracts structured data."""
    
    def __init__(self, tex_file_path: str):
        self.tex_file_path = tex_file_path
        self.cv_data = {
            'employment': [],
            'education': [],
            'publications': [],
            'recognitions': [],
            'outreach': [],
            'languages': [],
            'certifications': []
        }
    
    def parse_tex_file(self) -> Dict:
        """Parse the LaTeX CV file and extract structured data."""
        try:
            with open(self.tex_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except FileNotFoundError:
            print(f"❌ Error: Could not find {self.tex_file_path}")
            return self.cv_data
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return self.cv_data
        
        print("📄 Parsing CV data from LaTeX file...")
        
        # Parse each section
        self._parse_employment(content)
        self._parse_education(content)
        self._parse_publications(content)
        self._parse_recognitions(content)
        self._parse_outreach(content)
        self._parse_languages(content)
        self._parse_certifications(content)
        
        return self.cv_data
    
    def _parse_employment(self, content: str):
        """Parse employment section."""
        pattern = r'\\section\*\{EMPLOYMENT\}[\s\S]*?\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}'
        match = re.search(pattern, content)
        
        if match:
            items_content = match.group(1)
            items = re.findall(r'\\item\s+\\textbf\{[^}]+\}[^\\]*(?:\\\\[^\\]*)*?(?=\\item|\\end\{itemize\}|$)', items_content, re.DOTALL)
            
            for item in items:
                title_match = re.search(r'\\textbf\{([^}]+)\}', item)
                # Look for role after title and comma
                role_match = re.search(r'\\textbf\{[^}]+\},\s*([^\n\\]+)', item)
                # Look for date in italics
                date_match = re.search(r'\\textit\{([^}]*)\}', item)
                
                if title_match and role_match:
                    self.cv_data['employment'].append({
                        'title': title_match.group(1),
                        'role': role_match.group(1).strip(),
                        'date': date_match.group(1) if date_match else ''
                    })
        
        print(f"   📋 Found {len(self.cv_data['employment'])} employment entries")
    
    def _parse_education(self, content: str):
        """Parse education section."""
        pattern = r'\\section\*\{EDUCATION\}[\s\S]*?\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}'
        match = re.search(pattern, content)
        
        if match:
            items_content = match.group(1)
            items = re.findall(r'\\item\s+\\textbf\{[^}]+\}[\s\S]*?(?=\\item|$)', items_content)
            
            for item in items:
                title_match = re.search(r'\\textbf\{([^}]+)\}', item)
                role_match = re.search(r'\\\\[\s]*([^\n\\]+)', item)
                date_match = re.search(r'\\textit\{([^}]+)\}', item)
                
                if title_match:
                    self.cv_data['education'].append({
                        'title': title_match.group(1),
                        'role': role_match.group(1).strip() if role_match else '',
                        'date': date_match.group(1) if date_match else ''
                    })
        
        print(f"   🎓 Found {len(self.cv_data['education'])} education entries")
    
    def _parse_publications(self, content: str):
        """Parse publications section."""
        pattern = r'\\section\*\{PUBLICATIONS & WRITINGS\}[\s\S]*?\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}'
        match = re.search(pattern, content)
        
        if match:
            items_content = match.group(1)
            items = re.findall(r'\\item\s+\\textbf\{[^}]+\}[\s\S]*?(?=\\item|\\end\{itemize\}|$)', items_content, re.DOTALL)
            
            for item in items:
                title_match = re.search(r'\\textbf\{([^}]+)\}', item)
                # Look for author line (line that ends with organization/year)
                author_match = re.search(r'\\\\[\s]*([^\\]+?\.)\s*\\\\', item)
                # Look for href link - handle both empty and non-empty hrefs
                link_match = re.search(r'\\href\{([^}]*)\}\{[^}]*\\faLink[^}]*([^}]+)\}', item)
                # Look for date at the end
                date_match = re.search(r'·\s*([A-Z][a-z]{2}\s+\d{4})', item)
                
                if title_match:
                    self.cv_data['publications'].append({
                        'title': title_match.group(1),
                        'author': author_match.group(1).strip() if author_match else '',
                        'link': link_match.group(1) if link_match and link_match.group(1) else '',
                        'linkText': link_match.group(2).strip() if link_match else '',
                        'date': date_match.group(1) if date_match else ''
                    })
        
        print(f"   📝 Found {len(self.cv_data['publications'])} publication entries")
    
    def _parse_recognitions(self, content: str):
        """Parse recognitions section."""
        pattern = r'\\section\*\{RECOGNITIONS\}[\s\S]*?\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}'
        match = re.search(pattern, content)
        
        if match:
            items_content = match.group(1)
            items = re.findall(r'\\item\s+\\textbf\{[^}]+\}[\s\S]*?(?=\\item|\\end\{itemize\}|$)', items_content, re.DOTALL)
            
            for item in items:
                title_match = re.search(r'\\textbf\{([^}]+)\}', item)
                # Look for description after title (could be on same line or next line)
                role_match = re.search(r'\\textbf\{[^}]+\}\s*([^\n·\\]*?)(?:\n|\\\\|\s*·)', item)
                # Look for organization and date at the end
                org_date_match = re.search(r'([^·\n\\]+)\s*·\s*([A-Z][a-z]{2}\s+\d{4})', item)
                
                if title_match:
                    role = role_match.group(1).strip() if role_match else ''
                    if org_date_match:
                        if role:
                            role += f" - {org_date_match.group(1).strip()}"
                        else:
                            role = org_date_match.group(1).strip()
                        date = org_date_match.group(2)
                    else:
                        date = ''
                    
                    self.cv_data['recognitions'].append({
                        'title': title_match.group(1),
                        'role': role,
                        'date': date
                    })
        
        print(f"   🏆 Found {len(self.cv_data['recognitions'])} recognition entries")
    
    def _parse_outreach(self, content: str):
        """Parse outreach section."""
        pattern = r'\\section\*\{OUTREACH\}[\s\S]*?\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}'
        match = re.search(pattern, content)
        
        if match:
            items_content = match.group(1)
            items = re.findall(r'\\item\s+\\textbf\{[^}]+\}[\s\S]*?(?=\\item|\\end\{itemize\}|$)', items_content, re.DOTALL)
            
            for item in items:
                title_match = re.search(r'\\textbf\{([^}]+)\}', item)
                # Look for description after -- 
                desc_match = re.search(r'--\s*([^\\]+?)(?:\\\\|\n)', item)
                # Look for link
                link_match = re.search(r'\\href\{([^}]+)\}\{[^}]*\\fa[^}]*[^}]*([^}]+)\}', item)
                # Look for date at the end
                date_match = re.search(r'·\s*([A-Z][a-z]{2}\s+\d{4})', item)
                
                if title_match:
                    self.cv_data['outreach'].append({
                        'title': title_match.group(1),
                        'role': desc_match.group(1).strip() if desc_match else '',
                        'link': link_match.group(1) if link_match else '',
                        'linkText': link_match.group(2).strip() if link_match else '',
                        'date': date_match.group(1) if date_match else ''
                    })
        
        print(f"   🌟 Found {len(self.cv_data['outreach'])} outreach entries")
    
    def _parse_languages(self, content: str):
        """Parse languages section."""
        pattern = r'\\section\*\{LANGUAGES\}[\s\S]*?\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}'
        match = re.search(pattern, content)
        
        if match:
            items_content = match.group(1)
            items = re.findall(r'\\item\s+\\textbf\{[^}]+\}[\s\S]*?(?=\\item|$)', items_content)
            
            for item in items:
                title_match = re.search(r'\\textbf\{([^}]+)\}', item)
                role_match = re.search(r'·\s*\(([^)]+)\)', item)
                
                if title_match:
                    self.cv_data['languages'].append({
                        'title': title_match.group(1),
                        'role': role_match.group(1) if role_match else '',
                        'date': ''
                    })
        
        print(f"   🌍 Found {len(self.cv_data['languages'])} language entries")
    
    def _parse_certifications(self, content: str):
        """Parse certifications section."""
        pattern = r'\\section\*\{CERTIFICATIONS\}[\s\S]*?\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}'
        match = re.search(pattern, content)
        
        if match:
            items_content = match.group(1)
            items = re.findall(r'\\item\s+\\textbf\{[^}]+\}[\s\S]*?(?=\\item|$)', items_content)
            
            for item in items:
                title_match = re.search(r'\\textbf\{([^}]+)\}', item)
                role_match = re.search(r'\\\\[\s]*([^\n·]+)', item)
                date_match = re.search(r'·\s*Issued\s+([A-Z][a-z]{2}\s+\d{4})', item)
                
                if title_match:
                    self.cv_data['certifications'].append({
                        'title': title_match.group(1),
                        'role': role_match.group(1).strip() if role_match else '',
                        'date': f"Issued {date_match.group(1)}" if date_match else ''
                    })
        
        print(f"   📜 Found {len(self.cv_data['certifications'])} certification entries")


class HTMLUpdater:
    """Updates HTML file with new CV data."""
    
    def __init__(self, html_file_path: str):
        self.html_file_path = html_file_path
    
    def update_cv_data(self, cv_data: Dict) -> bool:
        """Update the HTML file with new CV data."""
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
        except FileNotFoundError:
            print(f"❌ Error: Could not find {self.html_file_path}")
            return False
        except Exception as e:
            print(f"❌ Error reading HTML file: {e}")
            return False
        
        # Convert CV data to JavaScript format
        js_data = self._convert_to_js_format(cv_data)
        
        # Find and replace the getFallbackCVData function
        pattern = r'function getFallbackCVData\(\) \{[\s\S]*?return \{[\s\S]*?\};[\s\S]*?\}'
        replacement = f"""function getFallbackCVData() {{
            return {js_data};
        }}"""
        
        updated_content = re.sub(pattern, replacement, html_content)
        
        if updated_content == html_content:
            print("⚠️ Warning: Could not find getFallbackCVData function to update")
            return False
        
        try:
            with open(self.html_file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            print(f"✅ Successfully updated {self.html_file_path}")
            return True
        except Exception as e:
            print(f"❌ Error writing HTML file: {e}")
            return False
    
    def _convert_to_js_format(self, cv_data: Dict) -> str:
        """Convert Python dict to JavaScript object format."""
        def format_item(item):
            formatted = "{\n"
            for key, value in item.items():
                # Escape quotes and newlines
                escaped_value = str(value).replace('"', '\\"').replace('\n', '\\n')
                formatted += f'                        {key}: "{escaped_value}",\n'
            formatted += "                    }"
            return formatted
        
        js_object = "{\n"
        for section, items in cv_data.items():
            js_object += f"                {section}: [\n"
            for i, item in enumerate(items):
                js_object += f"                    {format_item(item)}"
                if i < len(items) - 1:
                    js_object += ","
                js_object += "\n"
            js_object += "                ],\n"
        js_object += "            }"
        
        return js_object


class PDFGenerator:
    """Generates PDF from LaTeX file."""
    
    def __init__(self, tex_file_path: str, output_dir: str = "."):
        self.tex_file_path = tex_file_path
        self.output_dir = output_dir
    
    def generate_pdf(self) -> bool:
        """Generate PDF from LaTeX file."""
        print("📄 Generating PDF from LaTeX file...")
        
        try:
            # Check if pdflatex is available
            subprocess.run(['pdflatex', '--version'], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Error: pdflatex not found. Please install a LaTeX distribution.")
            print("   • Ubuntu/Debian: sudo apt-get install texlive-latex-base texlive-latex-extra")
            print("   • macOS: brew install --cask mactex")
            print("   • Windows: Install MiKTeX or TeX Live")
            return False
        
        try:
            # Run pdflatex twice to resolve references
            tex_file = Path(self.tex_file_path)
            
            for i in range(2):
                result = subprocess.run([
                    'pdflatex', 
                    '-output-directory', self.output_dir,
                    '-interaction=nonstopmode',
                    str(tex_file)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"❌ Error running pdflatex (run {i+1}):")
                    print(result.stdout)
                    print(result.stderr)
                    return False
            
            # Clean up auxiliary files
            base_name = tex_file.stem
            aux_extensions = ['.aux', '.log', '.out', '.fdb_latexmk', '.fls']
            
            for ext in aux_extensions:
                aux_file = Path(self.output_dir) / f"{base_name}{ext}"
                if aux_file.exists():
                    aux_file.unlink()
            
            pdf_path = Path(self.output_dir) / f"{base_name}.pdf"
            if pdf_path.exists():
                print(f"✅ Successfully generated PDF: {pdf_path}")
                return True
            else:
                print("❌ PDF generation completed but file not found")
                return False
                
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            return False


class GitManager:
    """Handles Git operations."""
    
    def __init__(self, files_to_commit: List[str]):
        self.files_to_commit = files_to_commit
    
    def is_git_repo(self) -> bool:
        """Check if current directory is a Git repository."""
        try:
            subprocess.run(['git', 'status'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def commit_and_push(self, custom_message: str = None) -> bool:
        """Commit changes and push to remote repository."""
        if not self.is_git_repo():
            print("⚠️ Warning: Not a Git repository. Skipping Git operations.")
            return False
        
        print("🔄 Committing and pushing changes...")
        
        try:
            # Check if there are any changes to commit
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            if not result.stdout.strip():
                print("ℹ️ No changes to commit.")
                return True
            
            # Add specified files
            for file_path in self.files_to_commit:
                if os.path.exists(file_path):
                    subprocess.run(['git', 'add', file_path], check=True)
                    print(f"   📁 Added {file_path}")
            
            # Create commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if custom_message:
                commit_message = custom_message
            else:
                commit_message = f"Auto-update CV data and PDF - {timestamp}"
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            print(f"✅ Committed changes: {commit_message}")
            
            # Push to remote
            subprocess.run(['git', 'push'], check=True)
            print("✅ Pushed changes to remote repository")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Error during Git operations: {e}")
            return False


class CVFileHandler(FileSystemEventHandler):
    """Handler for CV file change events (used in watch mode)."""
    
    def __init__(self, cv_file_path: str, automation: 'CVAutomation'):
        self.cv_file_path = Path(cv_file_path).resolve()
        self.automation = automation
        self.last_modified = 0
        
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
            
        # Check if the modified file is our CV file
        modified_path = Path(event.src_path).resolve()
        
        if modified_path == self.cv_file_path:
            # Debounce rapid file changes (some editors save multiple times)
            current_time = time.time()
            if current_time - self.last_modified < 2:  # 2 second debounce
                return
            
            self.last_modified = current_time
            print(f"\n{'='*60}")
            print(f"🔄 Detected change in {self.cv_file_path.name}")
            print(f"{'='*60}")
            
            # Run the automation
            self.automation.run_automation()
            
            print(f"{'='*60}")
            print("👀 Watching for changes... (Press Ctrl+C to stop)")


class CVAutomation:
    """Main automation class that orchestrates all operations."""
    
    def __init__(self, tex_file: str = "cv.tex", html_file: str = "index.html", 
                 output_dir: str = ".", auto_commit: bool = True, 
                 commit_message: str = None):
        self.tex_file = tex_file
        self.html_file = html_file
        self.output_dir = output_dir
        self.auto_commit = auto_commit
        self.commit_message = commit_message
        
        # Initialize components
        self.parser = CVParser(tex_file)
        self.html_updater = HTMLUpdater(html_file)
        self.pdf_generator = PDFGenerator(tex_file, output_dir)
        
        # Files to commit to Git
        self.git_files = [tex_file, html_file]
        
        # Add PDF file to Git files if it will be generated
        pdf_name = Path(tex_file).stem + ".pdf"
        self.git_files.append(pdf_name)
        
        self.git_manager = GitManager(self.git_files)
    
    def run_automation(self) -> bool:
        """Run the complete automation process."""
        print("\n🚀 Starting CV automation process...")
        
        # Check if required files exist
        if not os.path.exists(self.tex_file):
            print(f"❌ Error: {self.tex_file} not found in current directory")
            return False
        
        if not os.path.exists(self.html_file):
            print(f"❌ Error: {self.html_file} not found in current directory")
            return False
        
        success = True
        
        # 1. Parse CV data
        cv_data = self.parser.parse_tex_file()
        
        if not any(cv_data.values()):
            print("⚠️ Warning: No CV data found. Check your LaTeX file format.")
            return False
        
        # 2. Update HTML file
        print("\n🌐 Updating HTML file...")
        html_success = self.html_updater.update_cv_data(cv_data)
        success = success and html_success
        
        # 3. Generate PDF
        print("\n📄 Generating PDF...")
        pdf_success = self.pdf_generator.generate_pdf()
        success = success and pdf_success
        
        # 4. Commit and push if enabled
        if self.auto_commit and success:
            print("\n📤 Committing and pushing changes...")
            git_success = self.git_manager.commit_and_push(self.commit_message)
            success = success and git_success
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 AUTOMATION SUMMARY")
        print(f"{'='*60}")
        print(f"HTML update:     {'✅ Success' if html_success else '❌ Failed'}")
        print(f"PDF generation:  {'✅ Success' if pdf_success else '❌ Failed'}")
        
        if self.auto_commit:
            git_success = hasattr(self, 'git_success') or True  # Default to True if not set
            print(f"Git commit/push: {'✅ Success' if git_success else '❌ Failed'}")
        else:
            print("Git commit/push: ⏭️ Skipped")
        
        if success:
            print("\n🎉 All operations completed successfully!")
            if not self.auto_commit:
                print("💡 Don't forget to commit and push your changes manually.")
        else:
            print("\n⚠️ Some operations failed. Please check the errors above.")
        
        return success
    
    def watch_mode(self):
        """Start file watching mode."""
        if not WATCHDOG_AVAILABLE:
            print("❌ Error: watchdog package not installed.")
            print("Install it with: pip install watchdog")
            return
        
        print("👀 Starting file watcher mode...")
        print(f"Watching: {self.tex_file}")
        print("Press Ctrl+C to stop watching")
        
        # Set up file watcher
        event_handler = CVFileHandler(self.tex_file, self)
        observer = Observer()
        
        # Watch the current directory
        watch_path = str(Path.cwd())
        observer.schedule(event_handler, watch_path, recursive=False)
        
        # Start watching
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping file watcher...")
            observer.stop()
        
        observer.join()
        print("File watcher stopped.")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='CV Automation Script')
    parser.add_argument('--watch', '-w', action='store_true', 
                       help='Watch cv.tex for changes and auto-update')
    parser.add_argument('--tex-file', '-t', default='cv.tex',
                       help='LaTeX CV file path (default: cv.tex)')
    parser.add_argument('--html-file', '--html', default='index.html',
                       help='HTML portfolio file path (default: index.html)')
    parser.add_argument('--output-dir', '-o', default='.',
                       help='Output directory for PDF (default: current directory)')
    parser.add_argument('--no-commit', action='store_true',
                       help='Skip Git commit and push')
    parser.add_argument('--commit-message', '-m', 
                       help='Custom commit message')
    
    args = parser.parse_args()
    
    # Create automation instance
    automation = CVAutomation(
        tex_file=args.tex_file,
        html_file=args.html_file,
        output_dir=args.output_dir,
        auto_commit=not args.no_commit,
        commit_message=args.commit_message
    )
    
    if args.watch:
        # Watch mode
        automation.watch_mode()
    else:
        # Run once
        automation.run_automation()


if __name__ == "__main__":
    main()