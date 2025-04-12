import streamlit as st
import openai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import time
import re
import random

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Email sender configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

def generate_blog_post(product_name, product_description, keywords, tone="informative"):
    """Generate a SEO-optimized blog post using OpenAI."""
    
    # Create a system prompt with SEO best practices
    system_prompt = """
    You are an expert garden marketing copywriter and SEO specialist. Write engaging, informative content for 
    home gardening enthusiasts that naturally incorporates keywords while providing genuine value.
    
    Follow these SEO best practices:
    - Create an attention-grabbing H1 title (60-65 characters) with the primary keyword
    - Include H2 and H3 subheadings with secondary keywords
    - Write 800-1200 words of informative content
    - Use bullet points and numbered lists where appropriate
    - Naturally integrate keywords (don't overuse them)
    - Include a compelling call-to-action featuring the product
    - Follow a structure: intro, problem, solution (featuring product), how-to section, benefits, conclusion
    
    Format the output as Markdown.
    """
    
    # Create user prompt with the product and keywords
    user_prompt = f"""
    Write a comprehensive blog post about gardening that promotes {product_name}.
    
    Product description: {product_description}
    
    Incorporate these keywords naturally throughout the post: {', '.join(keywords)}
    
    The tone should be {tone} and connect with home gardening enthusiasts.
    
    Make sure to:
    1. Include practical gardening tips related to the product
    2. Explain benefits of using the product without being overly promotional
    3. Include a section on sustainable gardening practices
    4. End with a subtle call-to-action to learn more about the product
    """
    
    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        # Extract and return the blog post content
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating blog post: {str(e)}"

def generate_social_media_posts(product_name, product_description, keywords, platform="mixed", num_posts=4):
    """Generate social media posts for the specified platform."""
    
    emoji_sets = [
        "🌱 🌿 🍃 🌲 🌳 🌴 🌵 🌾 🌷 🌻",
        "🧑‍🌾 👩‍🌾 🌱 🪴 🌿 🍀 💐 🌼 🏡 💦",
        "🌈 🌞 🌧️ 🌷 🌻 🌸 🌹 🌺 🌼 🪴",
        "♻️ 🌎 🌍 🌏 🌱 🪴 🌿 🌲 🍃 💚"
    ]
    
    system_prompt = f"""
    You are a social media marketing expert for a home gardening brand. Create engaging, conversion-focused 
    social media posts for {platform} that promote gardening products. 
    
    Each post should:
    - Be the optimal length for the platform (shorter for X/Twitter, medium for Instagram)
    - Include relevant and trending hashtags (5-7 for Instagram, 2-3 for X/Twitter)
    - Incorporate emojis naturally
    - Have a clear call-to-action
    - Include a hook that captures attention immediately
    
    Use some of these relevant emojis: {random.choice(emoji_sets)}
    """
    
    user_prompt = f"""
    Create {num_posts} engaging social media posts promoting {product_name}.
    
    Product description: {product_description}
    
    Incorporate these keywords naturally: {', '.join(keywords)}
    
    For each post:
    1. Start with an attention-grabbing first line
    2. Highlight a key benefit of the product
    3. Include relevant hashtags
    4. End with a clear call-to-action
    
    Format each post as a separate numbered item.
    """
    
    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=1000
        )
        
        # Extract and return the social media posts
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating social media posts: {str(e)}"

def send_email(recipient_email, subject, blog_post, social_posts):
    """Send the generated content to the specified email address."""
    try:
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_SENDER
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Create the HTML content
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #2E7D32; border-bottom: 2px solid #2E7D32; padding-bottom: 10px; }}
                h2 {{ color: #388E3C; }}
                .blog-section {{ margin-bottom: 30px; background-color: #F1F8E9; padding: 15px; border-radius: 8px; }}
                .social-section {{ margin-bottom: 30px; background-color: #E8F5E9; padding: 15px; border-radius: 8px; }}
                .post {{ background-color: white; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Your Garden Marketing Content</h1>
                
                <div class="blog-section">
                    <h2>Blog Post</h2>
                    <div class="post">
                        {blog_post.replace('\n', '<br>')}
                    </div>
                </div>
                
                <div class="social-section">
                    <h2>Social Media Posts</h2>
                    <div class="post">
                        {social_posts.replace('\n', '<br>')}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(html, 'html'))
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

def main():
    st.set_page_config(
        page_title="Garden Content Generator",
        page_icon="🌱",
        layout="wide"
    )
    
    st.title("🌱 Garden Content Generator")
    st.subheader("Create SEO-optimized content for your gardening products")
    
    with st.expander("📋 Instructions", expanded=True):
        st.markdown("""
        This tool generates SEO-optimized blog posts and social media content for your gardening products.
        
        1. Enter your product name
        2. Add a brief product description (1-2 lines)
        3. Add keywords (one per line)
        4. Configure content settings
        5. Enter your email address
        6. Click 'Generate Content'
        
        The generated content will be sent to your email address.
        """)
    
    # Input form
    with st.form("content_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Product Name", placeholder="e.g., Organic Root Booster")
            product_description = st.text_area(
                "Product Description (1-2 lines)", 
                placeholder="A nutrient-rich organic fertilizer that enhances root development and improves plant health."
            )
            keywords = st.text_area(
                "Keywords (one per line)", 
                placeholder="organic gardening\nsoil health\nroot development\netc."
            )
        
        with col2:
            tone_options = ["Informative", "Conversational", "Professional", "Enthusiastic"]
            tone = st.selectbox("Blog Post Tone", tone_options)
            
            platform_options = ["Instagram", "X (Twitter)", "Mixed"]
            platform = st.selectbox("Social Media Platform", platform_options)
            
            num_posts = st.slider("Number of Social Media Posts", 2, 8, 4)
            
            email = st.text_input("Your Email Address", placeholder="example@email.com")
        
        submit_button = st.form_submit_button("Generate Content")
    
    # Process form submission
    if submit_button:
        if not product_name or not product_description or not keywords or not email:
            st.error("Please fill in all required fields.")
            return
        
        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            st.error("Please enter a valid email address.")
            return
        
        # Convert keywords from textarea to list
        keyword_list = [k.strip() for k in keywords.split('\n') if k.strip()]
        
        if len(keyword_list) < 2:
            st.error("Please enter at least 2 keywords.")
            return
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Generate blog post
        status_text.text("Generating blog post...")
        blog_post = generate_blog_post(product_name, product_description, keyword_list, tone.lower())
        progress_bar.progress(40)
        
        # Generate social media posts
        status_text.text("Creating social media content...")
        social_posts = generate_social_media_posts(
            product_name,
            product_description,
            keyword_list, 
            platform.lower().split(' ')[0], 
            num_posts
        )
        progress_bar.progress(80)
        
        # Send email
        status_text.text("Sending email...")
        email_subject = f"Garden Content for {product_name} - {time.strftime('%Y-%m-%d')}"
        success, message = send_email(email, email_subject, blog_post, social_posts)
        progress_bar.progress(100)
        
        if success:
            st.success(f"✅ {message} Check your inbox for the generated content.")
        else:
            st.error(message)
            
            # Display the content on the page as fallback
            st.subheader("Generated Blog Post")
            st.markdown(blog_post)
            
            st.subheader("Generated Social Media Posts")
            st.markdown(social_posts)
        
        # Clear progress indicators after 3 seconds
        time.sleep(3)
        progress_bar.empty()
        status_text.empty()

if __name__ == "__main__":
    main()