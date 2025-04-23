# Customization Guide for Your Geoglypha Website

This document provides guidance on how to customize your index.html homepage to match your specific needs and preferences.

## Basic Customization

### Changing the Title

To change the website title, modify the `<title>` tag in the `<head>` section:

```html
<title>Your Custom Title Here</title>
```

### Customizing Colors

The website uses CSS variables for consistent coloring. You can modify these variables in the `:root` selector at the beginning of the CSS:

```css
:root {
    --primary-color: #3a6351;    /* Main color for headers and footers */
    --secondary-color: #f2edd7;  /* Background color for some sections */
    --accent-color: #a0937d;     /* Color for buttons and highlights */
    --text-color: #333;          /* Main text color */
    --light-text: #f5f5f5;       /* Text color on dark backgrounds */
    --header-font: 'Georgia', serif;
    --body-font: 'Arial', sans-serif;
}
```

### Changing Fonts

You can change the fonts by modifying the font variables in the `:root` selector:

```css
--header-font: 'Your Preferred Header Font', serif;
--body-font: 'Your Preferred Body Font', sans-serif;
```

For web fonts, you'll need to add the appropriate `<link>` tag in the `<head>` section. For example, to use Google Fonts:

```html
<link href="https://fonts.googleapis.com/css2?family=Roboto&family=Playfair+Display&display=swap" rel="stylesheet">
```

Then update your CSS variables:

```css
--header-font: 'Playfair Display', serif;
--body-font: 'Roboto', sans-serif;
```

## Replacing Images

The template uses placeholder images that you should replace with your own. Here's how to replace each image:

### Hero Image

Find this section in the CSS:

```css
.hero {
    background-image: url('https://via.placeholder.com/1600x900/3a6351/f5f5f5?text=Ancient+Landscapes');
}
```

Replace the URL with the path to your image in your Google Cloud Storage bucket:

```css
.hero {
    background-image: url('your-hero-image.jpg');
}
```

### Feature Cards Images

For each feature card, find the corresponding `feature-img` div and replace the background-image URL:

```html
<div class="feature-img" style="background-image: url('your-archaeology-image.jpg');"></div>
```

### Project Cards Images

Similarly, for each project card, replace the background-image URL:

```html
<div class="project-img" style="background-image: url('your-cahokia-image.jpg');"></div>
```

### About Section Image

Find the about-img class in the CSS and replace the background-image URL:

```css
.about-img {
    background-image: url('your-about-image.jpg');
}
```

## Adding Content

### Modifying Text

You can easily modify any text content by editing the HTML. For example, to change the hero section text:

```html
<h1>Your Custom Headline Here</h1>
<p>Your custom description text goes here.</p>
```

### Adding New Projects

To add a new project, copy an existing project card and modify it:

```html
<div class="project-card">
    <div class="project-img" style="background-image: url('your-new-project-image.jpg');"></div>
    <div class="project-content">
        <h3>Your New Project Title</h3>
        <p>Description of your new project.</p>
        <a href="your-new-project.html" class="btn">Explore</a>
    </div>
</div>
```

### Adding New Navigation Links

To add a new page to the navigation menu, add a new list item to the navigation list:

```html
<li><a href="your-new-page.html">Your New Page</a></li>
```

Also add it to the footer quick links:

```html
<li><a href="your-new-page.html">Your New Page</a></li>
```

## Advanced Customization

### Adding Custom JavaScript

You can add custom JavaScript at the end of the file before the closing `</body>` tag:

```html
<script>
    // Your custom JavaScript here
</script>
```

### Adding External Libraries

To add external libraries, include them in the `<head>` section:

```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/some-library/1.0.0/library.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/some-library/1.0.0/library.min.js"></script>
```

### Adding Google Analytics

To add Google Analytics, insert the following code just before the closing `</head>` tag:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR-GA-ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'YOUR-GA-ID');
</script>
```

## Integration with Google Earth Engine

For your future plans to integrate Google Earth Engine API, you'll need to:

1. Add the Earth Engine JavaScript API to your HTML:

```html
<script src="https://cdn.jsdelivr.net/npm/earthengine-api@0.1.232/build/earthengine-api.min.js"></script>
```

2. Create a separate JavaScript file for your Earth Engine code and link it:

```html
<script src="gee-tools.js"></script>
```

## Uploading to Google Cloud Storage

After making your customizations:

1. Upload all your files (HTML, CSS, JavaScript, images) to your Google Cloud Storage bucket `geoglypha1`
2. Make sure all files are set to be publicly accessible
3. Your homepage will be available at: https://storage.googleapis.com/geoglypha1/index.html
4. Your Cahokia page will be available at: https://storage.googleapis.com/geoglypha1/cahokia.html

## Additional Resources

- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Google Earth Engine API Documentation](https://developers.google.com/earth-engine)
- [Web Development Resources](https://developer.mozilla.org/en-US/docs/Web)
