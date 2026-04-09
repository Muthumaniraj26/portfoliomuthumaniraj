import os
import re
import yaml
import glob
from pathlib import Path
import markdown

projects_dir = r"d:\portfolio\_projects"
internships_dir = r"d:\portfolio\_internships"
site_projects_dir = r"d:\portfolio\_site\projects"
site_internships_dir = r"d:\portfolio\_site\internships"
site_index_file = r"d:\portfolio\_site\index.html"
layout_file = r"d:\portfolio\_layouts\project.html"
internship_layout_file = r"d:\portfolio\_layouts\internship.html"

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

def render_md(text):
    return markdown.markdown(text)

project_html_template = """<article class="project-page" style="max-width: 900px; margin: 0 auto; padding: 2rem;">
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

internship_html_template = """<article class="project-page" style="max-width: 950px; margin: 0 auto; padding: 2rem; animation: fadeInScale 0.8s ease-out;">
        <header class="project-header" style="text-align: center; margin-bottom: 4rem; position: relative;">
          <div style="position: absolute; top: -50px; left: 50%; transform: translateX(-50%); width: 300px; height: 300px; background: var(--accent-color); filter: blur(120px); opacity: 0.15; z-index: -1;"></div>
          <img src="{logo}" alt="{company} logo" style="width: 160px; height: 160px; border-radius: 24px; margin-bottom: 2.5rem; object-fit: contain; background: #fff; padding: 15px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 10px 40px rgba(0,0,0,0.4);">
          <h1 style="font-size: 3.2rem; margin-bottom: 0.8rem; color: #fff; font-weight: 800; letter-spacing: -0.03em;">{title}</h1>
          <p class="tagline" style="font-size: 1.3rem; color: #aaa; font-weight: 500;">
            <i class="fas fa-at" style="color: var(--accent-color); opacity: 0.7;"></i> <a href="{company_url}" target="_blank" style="color: var(--accent-color); text-decoration: none; font-weight: 700;">{company}</a> 
            <span style="margin: 0 15px; opacity: 0.3;">|</span> 
            <i class="far fa-calendar-alt" style="opacity: 0.5;"></i> {duration}
          </p>
          <div class="action-buttons" style="margin-top: 2.5rem; display: flex; justify-content: center; gap: 1.5rem;">
            {cert_html}
            {github_html}
          </div>
        </header>
        <div class="project-content" style="line-height: 1.8; font-size: 1.2rem; color: #ccc; margin-bottom: 4rem; background: rgba(255,255,255,0.03); padding: 3rem; border-radius: 24px; border: 1px solid rgba(255,255,255,0.05); backdrop-filter: blur(10px);">
          {content_html}
        </div>
        <div class="project-meta" style="background: linear-gradient(135deg, rgba(30,30,30,0.8), rgba(20,20,20,0.8)); padding: 2.5rem; border-radius: 24px; border: 1px solid rgba(255,255,255,0.05); backdrop-filter: blur(10px);">
          <h3 style="color: var(--accent-color); margin-top: 0; margin-bottom: 2rem; display: flex; align-items: center; gap: 12px; font-size: 1.5rem;">
            <i class="fas fa-brain"></i> Core Expertise & Technologies
          </h3>
          <div class="pill-container" style="display: flex; flex-wrap: wrap; gap: 12px;">
            {skills_html}
          </div>
        </div>
        <footer style="text-align: center; margin-top: 5rem; padding-bottom: 3rem;">
          <a href="/#internships" class="internship-btn" style="display: inline-flex; align-items: center; gap: 10px; padding: 12px 30px; border-radius: 40px; border: 1px solid rgba(255,255,255,0.1); color: #fff; text-decoration: none; font-weight: 600; background: rgba(255,255,255,0.05); transition: all 0.3s ease;">
            <i class="fas fa-arrow-left"></i> Back to Experience
          </a>
        </footer>
      </article>"""

# Add robust wrapper for stand-alone pages (matches default.html layout)
PAGE_WRAPPER = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{title}} | Portfolio</title>
  <link rel="stylesheet" href="/assets/css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" />
  <link rel="stylesheet" type='text/css' href="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/devicon.min.css" />
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
</head>
<body style="background: #121212; color: #e0e0e0; margin: 0;">
    <div class="site-wrapper">
      <aside class="sidebar">
        <div class="sidebar-content">
          <img src="/assets/images/profile.jpeg" alt="Profile" class="profile-photo" style="width: 150px; height: 150px; border-radius: 50%; border: 3px solid #007BFF; margin-bottom: 1.5rem; object-fit: cover;">
          <h1 style="font-size: 1.8rem; margin: 0; color: #fff;">Muthumaniraj Sanjeevi</h1>
          <p style="color: #888; font-size: 0.9rem; margin: 0.5rem 0 2rem 0;">A portfolio showcasing my projects and skills.</p>
          
          <nav class="sidebar-nav" style="display: flex; flex-direction: column; gap: 1rem; text-align: left; padding: 0 1rem;">
            <a href="/" style="color: #fff; text-decoration: none; font-weight: 500; display: flex; align-items: center; gap: 10px;">
              <i class="fas fa-home"></i> Home
            </a>
            <a href="https://github.com/Muthumaniraj26" target="_blank" style="color: #888; text-decoration: none; font-weight: 500; display: flex; align-items: center; gap: 10px;">
              <i class="devicon-github-original"></i> GitHub
            </a>
            <a href="https://www.youtube.com/@muthumanirajs" target="_blank" style="color: #888; text-decoration: none; font-weight: 500; display: flex; align-items: center; gap: 10px;">
              <i class="devicon-youtube-plain"></i> Youtube
            </a>
            <a href="https://medium.com/@muthumanirajs3" target="_blank" style="color: #888; text-decoration: none; font-weight: 500; display: flex; align-items: center; gap: 10px;">
              <i class="fab fa-medium"></i> Medium
            </a>
            <a href="https://www.linkedin.com/in/muthumaniraj-sanjeevi/" target="_blank" style="color: #888; text-decoration: none; font-weight: 500; display: flex; align-items: center; gap: 10px;">
              <i class="devicon-linkedin-plain"></i> LinkedIn
            </a>
          </nav>
        </div>
      </aside>
      
      <main class="main-content" style="margin-left: 350px; padding: 3rem;">
          {body}
      </main>
    </div>
</body>
</html>"""

def process_projects():
    for md_path in glob.glob(os.path.join(projects_dir, "*.md")):
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        yaml_str, body = extract_frontmatter(content)
        if not yaml_str: continue
        data = yaml.safe_load(yaml_str)
        slug = Path(md_path).stem
        site_html_path = os.path.join(site_projects_dir, slug, "index.html")
        if not os.path.exists(os.path.dirname(site_html_path)): os.makedirs(os.path.dirname(site_html_path))
        
        tagline_html = f'<p class="tagline" style="font-style: italic; font-size: 1.2rem; color: #888;">{data.get("tagline", "")}</p>' if data.get("tagline") else ""
        repo_html = f'<a href="{data["repo_url"]}" class="button" target="_blank" style="padding: 0.8rem 2rem; background-color: #007BFF; color: #fff; text-decoration: none; border-radius: 50px; font-weight: 600;">View Source Code</a>' if data.get("repo_url") else ""
        video_html = f'<div class="video-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin-bottom: 3rem; border-radius: 12px; box-shadow: 0 20px 40px rgba(0,0,0,0.5);"><iframe src="{data["video_embed_url"]}" frameborder="0" allowfullscreen style="position: absolute; top:0; left: 0; width: 100%; height: 100%;"></iframe></div>' if data.get("video_embed_url") else ""
        
        skills_html = ""
        if data.get('skills'): 
            pills = "".join([f'<span class="pill" style="display:inline-block; margin: 4px; padding: 5px 12px; background: rgba(0,123,255,0.1); color: #007BFF; border-radius: 20px; font-size: 0.9rem;">{s}</span>' for s in data['skills']])
            skills_html = f'<div style="flex: 1 1 300px; background-color: #1c1c1c; padding: 1.5rem; border-radius: 12px; border: 1px solid #333;"><h3 style="color: #007BFF; margin-top: 0;">Skills Applied</h3><div style="display:flex; flex-wrap:wrap;">{pills}</div></div>'

        tools_html = ""
        if data.get('tools'):
            tool_pills = "".join([f'<span class="pill" style="display:inline-block; margin: 4px; padding: 5px 12px; background: rgba(255,255,255,0.05); color: #e0e0e0; border-radius: 20px; font-size: 0.9rem; border: 1px solid #444;">{t}</span>' for t in data['tools']])
            tools_html = f'<div style="flex: 1 1 300px; background-color: #1c1c1c; padding: 1.5rem; border-radius: 12px; border: 1px solid #333;"><h3 style="color: #66b2ff; margin-top: 0;">Tools & Tech</h3><div style="display:flex; flex-wrap:wrap;">{tool_pills}</div></div>'

        collaborators_html = ""
        if data.get('collaborators'):
            collab_list = "".join([f'<li style="margin-bottom: 0.8rem;"><a href="https://github.com/{c.get("github_username", "")}" target="_blank" style="color: #007BFF; text-decoration: none; font-weight: 500;">{c.get("name", "Collaborator")}</a> <span style="color: #888; font-size: 0.9rem;">— {c.get("role", "")}</span></li>' for c in data['collaborators']])
            collaborators_html = f'<div style="flex: 1 1 300px; background-color: #1c1c1c; padding: 1.5rem; border-radius: 12px; border: 1px solid #333;"><h3 style="color: #007BFF; margin-top: 0;">Collaborators</h3><ul style="list-style: none; padding: 0; margin: 0;">{collab_list}</ul></div>'
            
        final_ui = project_html_template.format(
            title=data.get('title', ''), tagline_html=tagline_html, repo_html=repo_html,
            video_html=video_html, content_html=render_md(body), skills_html=skills_html,
            tools_html=tools_html, collaborators_html=collaborators_html
        )
        with open(site_html_path, 'w', encoding='utf-8') as f:
            f.write(PAGE_WRAPPER.format(title=data.get('title', ''), body=final_ui))

def process_internships():
    internships_list = []
    for md_path in sorted(glob.glob(os.path.join(internships_dir, "*.md")), reverse=True):
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        yaml_str, body = extract_frontmatter(content)
        if not yaml_str: continue
        data = yaml.safe_load(yaml_str)
        slug = Path(md_path).stem
        data['slug'] = slug
        data['content'] = render_md(body)
        internships_list.append(data)
        
        site_html_path = os.path.join(site_internships_dir, slug, "index.html")
        if not os.path.exists(os.path.dirname(site_html_path)): os.makedirs(os.path.dirname(site_html_path))
        
        cert_url = data.get("certificate_url", "#")
        repo_url = data.get("github_url", "#")
        
        cert_html = f'<a href="{cert_url}" class="internship-btn" target="_blank" style="padding: 0.8rem 2rem; background-color: #007BFF; color: #fff; text-decoration: none; border-radius: 5px;"><i class="fas fa-certificate"></i> View Certificate</a>' if cert_url != "#" else ""
        github_html = f'<a href="{repo_url}" class="internship-btn outline" target="_blank" style="padding: 0.8rem 2rem; border: 1px solid #007BFF; color: #007BFF; text-decoration: none; border-radius: 5px;"><i class="fab fa-github"></i> Project Repository</a>' if repo_url != "#" else ""
        
        skills_html = "".join([f'<span class="pill" style="display:inline-block; margin: 4px; padding: 5px 12px; background: rgba(0,123,255,0.1); color: #007BFF; border-radius: 20px; font-size: 0.9rem;">{s}</span>' for s in data.get('skills', [])])
        
        final_ui = internship_html_template.format(
            title=data.get('title', ''), company=data.get('company', ''),
            company_url=data.get('company_url', '#'),
            logo=data.get('logo', ''),
            duration=data.get('duration', ''), cert_html=cert_html,
            github_html=github_html, content_html=data['content'],
            skills_html=skills_html
        )
        with open(site_html_path, 'w', encoding='utf-8') as f:
            f.write(PAGE_WRAPPER.format(title=data.get('title', ''), body=final_ui))
    return internships_list

def update_homepage(internships):
    # Read the SOURCE index.html (content only)
    with open(os.path.join(os.path.dirname(site_index_file), "..", "index.html"), 'r', encoding='utf-8') as f:
        src_content = f.read()
    
    # Strip frontmatter
    _, body_content = extract_frontmatter(src_content)
    
    # 1. Update Internship Section within the body content
    cards = ""
    for idx, item in enumerate(internships):
        delay = idx * 0.1
        skills_pills = "".join([f'<span class="skill-pill">{s}</span>' for s in item.get('skills', [])])
        logo_html = f'<img src="{item["logo"]}" class="company-logo" alt="{item["company"]}">' if item.get("logo") else ""
        company_display = f'<a href="{item["company_url"]}" target="_blank" class="company-link">{item["company"]}</a>' if item.get("company_url") else f'<strong>{item["company"]}</strong>'
        
        cert_link = item.get('certificate_url', '#')
        github_link = item.get('github_url', '#')
        
        cards += f"""
      <div class="internship-card" style="animation-delay: {delay}s;">
        <div class="internship-header">
          <div class="header-left">
            {logo_html}
            <div class="header-info">
              <h3>{item['title']}</h3>
              <div class="internship-company">
                <i class="fas fa-building" style="font-size: 0.8rem; opacity: 0.6;"></i> {company_display}
                <span class="duration-small"><i class="far fa-calendar-alt"></i> {item['duration']}</span>
              </div>
            </div>
          </div>
          <div class="header-right">
            <a href="/internships/{item['slug']}/" class="internship-btn prime"><i class="fas fa-external-link-alt"></i> View Details</a>
          </div>
        </div>
        <div class="internship-actions">
          {f'<a href="{cert_link}" class="internship-btn" target="_blank"><i class="fas fa-award"></i> Certificate</a>' if cert_link != "#" else ""}
          {f'<a href="{github_link}" class="internship-btn" target="_blank"><i class="fab fa-github"></i> Project Repo</a>' if github_link != "#" else ""}
        </div>
        <div class="internship-skills">
          {skills_pills}
        </div>
      </div>"""
    
    # Inject cards into the body content (replacing the liquid-heavy container)
    body_content = re.sub(r'<div class="internship-container">.*?</div>', f'<div class="internship-container">{cards}\n  </div>', body_content, flags=re.DOTALL)
    
    # 2. Render simple Markdown/Liquid parts that aren't dynamic
    # (Handling the project loop is complex without Jekyll, so we'll preserve it if possible or just replace it)
    # For now, let's assume we want the homepage to look exactly like the build result.
    
    # 3. Final Wrap with PAGE_WRAPPER
    import time
    version = int(time.time())
    final_html = PAGE_WRAPPER.format(title="Home", body=body_content)
    
    # 4. Cache bust CSS in the final output
    final_html = re.sub(r'href="/assets/css/style\.css(\?v=[^"]+)?"', f'href="/assets/css/style.css?v={version}"', final_html)

    with open(site_index_file, 'w', encoding='utf-8') as f:
        f.write(final_html)

if __name__ == "__main__":
    process_projects()
    interns = process_internships()
    update_homepage(interns)
    print("UI and Layouts updated successfully.")
