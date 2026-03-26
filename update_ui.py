import os
import re
import yaml
import glob
from pathlib import Path

projects_dir = r"d:\portfolio\_projects"
site_projects_dir = r"d:\portfolio\_site\projects"
layout_file = r"d:\portfolio\_layouts\project.html"

# Default collaborator data if missing
DEFAULT_ROLE = "Developer & Contributor"
DEFAULT_BIO = "Specializing in software development and project execution."

def slugify(text):
    return re.sub(r'[^a-zA-Z0-9]+', '-', text.lower()).strip('-')

def extract_frontmatter(content):
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        return match.group(1), content[match.end():].strip()
    return None, content

html_template = """<article class="project-page" style="max-width: 900px; margin: 0 auto; padding: 2rem;">

        <header class="project-header" style="text-align: center; margin-bottom: 2rem;">
          <h1>{title}</h1>
          {tagline_html}

          <div class="action-buttons" style="margin-top: 1.5rem;">
            {repo_html}
          </div>
        </header>

        {video_html}

        <div class="project-content" style="line-height: 1.8; font-size: 1.15rem; color: #ddd;">
          {content_html}
        </div>

        <div class="project-meta">
          {skills_html}
          {tools_html}
        </div>

        {collaborators_html}

        <footer style="text-align: center; margin-top: 4rem; padding-bottom: 2rem;">
          <a href="/" style="color: #007BFF; text-decoration: none; font-weight: bold;">&larr; Back to Portfolio</a>
        </footer>
      </article>"""

def build_html(frontmatter, raw_content):
    pass

def process_project():
    for md_path in glob.glob(os.path.join(projects_dir, "*.md")):
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        yaml_str, body = extract_frontmatter(content)
        if not yaml_str: continue

        data = yaml.safe_load(yaml_str)
        slug = Path(md_path).stem

        # 1. Update frontmatter
        modified = False
        if 'collaborators' in data:
            for idx, collab in enumerate(data['collaborators']):
                if 'role' not in collab:
                    data['collaborators'][idx]['role'] = DEFAULT_ROLE
                    modified = True
                if 'bio' not in collab:
                    data['collaborators'][idx]['bio'] = DEFAULT_BIO
                    modified = True

        if modified:
            new_yaml = yaml.dump(data, sort_keys=False, allow_unicode=True)
            new_content = f"---\n{new_yaml}---\n{body}"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        
        # 2. Update _site file
        site_html_path = os.path.join(site_projects_dir, slug, "index.html")
        if not os.path.exists(site_html_path):
            continue
            
        with open(site_html_path, 'r', encoding='utf-8') as f:
            site_html = f.read()
            
        content_match = re.search(r'<div class="project-content".*?>(.*?)</div>\s*<div class="project-meta"', site_html, re.DOTALL)
        existing_content_html = content_match.group(1).strip() if content_match else "<p>No content available.</p>"
        
        tagline_html = f'<p class="tagline" style="font-style: italic; font-size: 1.2rem; color: #888;">{data.get("tagline", "")}</p>' if data.get("tagline") else ""
        repo_html = f'<a href="{data["repo_url"]}" class="button" target="_blank" style="padding: 0.8rem 2rem; background-color: #007BFF; color: #fff; text-decoration: none; border-radius: 50px; font-weight: 600;">View Source Code</a>' if data.get("repo_url") else ""
        video_html = f'<div class="video-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin-bottom: 3rem; border-radius: 12px; box-shadow: 0 20px 40px rgba(0,0,0,0.5);"><iframe src="{data["video_embed_url"]}" frameborder="0" allowfullscreen style="position: absolute; top:0; left: 0; width: 100%; height: 100%;"></iframe></div>' if data.get("video_embed_url") else ""
        
        skills_html = ""
        if data.get('skills'):
            pills = "".join([f'<span class="pill">{s}</span>' for s in data['skills']])
            skills_html = f'<div><h3 style="color: #007BFF; margin-top: 0;">Skills Applied</h3><div class="pill-container">{pills}</div></div>'
            
        tools_html = ""
        if data.get('tools'):
            pills = "".join([f'<span class="pill">{t}</span>' for t in data['tools']])
            tools_html = f'<div><h3 style="color: #007BFF; margin-top: 0;">Tools Used</h3><div class="pill-container">{pills}</div></div>'
            
        collaborators_html = ""
        if data.get('collaborators'):
            cards = ""
            for c in data['collaborators']:
                github = c.get('github_username', '')
                name = c.get('name', '')
                role = c.get('role', DEFAULT_ROLE)
                cards += f'<a href="https://github.com/{github}" target="_blank" class="github-card"><span class="external-icon">↗</span><img src="https://github.com/{github}.png" alt="{name}"><div class="github-card-info"><h4>{name}</h4><p>{role}</p><span class="github-handle">@{github}</span></div></a>'
            collaborators_html = f'<section class="collaborator-section"><h3 style="color: #fff; font-size: 1.5rem;">Project Contributors</h3><div class="collab-grid">{cards}</div></section>'
            
        final_ui = html_template.format(
            title=data.get('title', ''),
            tagline_html=tagline_html,
            repo_html=repo_html,
            video_html=video_html,
            content_html=existing_content_html,
            skills_html=skills_html,
            tools_html=tools_html,
            collaborators_html=collaborators_html
        )
        
        # Inject into site_html
        new_site_html = re.sub(
            r'<article class="project-page".*?</article>', 
            final_ui, 
            site_html, 
            flags=re.DOTALL
        )

        # Force cache bust for style.css
        new_site_html = re.sub(
            r'href="/assets/css/style\.css(\?v=[a-f0-9]+)?"', 
            'href="/assets/css/style.css?v=' + str(os.urandom(4).hex()) + '"', 
            new_site_html
        )

        with open(site_html_path, 'w', encoding='utf-8') as f:
            f.write(new_site_html)

if __name__ == "__main__":
    process_project()
    print("UI updated successfully.")
