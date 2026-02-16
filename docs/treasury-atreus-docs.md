# Treasury of Atreus 3D Model - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [File Structure](#file-structure)
3. [Deployment to Google Cloud](#deployment-to-google-cloud)
4. [Customizing the UI](#customizing-the-ui)
5. [Modifying the 3D Model](#modifying-the-3d-model)
6. [Troubleshooting](#troubleshooting)

---

## Overview

This is a Three.js-based interactive 3D model of the Treasury of Atreus (Tomb of Agamemnon) from Mycenae, Greece. The model features:
- Accurate architectural reconstruction with 33 corbelled stone courses
- Interactive camera controls
- Multiple viewing angles
- Toggle-able features (earth mound, rosettes, side chamber)
- Day/night lighting simulation
- Mobile-responsive design

**Technologies Used:**
- Three.js r160 (3D rendering)
- OrbitControls (camera interaction)
- Vanilla JavaScript (no frameworks required)
- CSS3 (styling and animations)

---

## File Structure

```
your-project/
├── index.html          # Main HTML file (complete standalone file)
├── README.md           # This documentation
└── assets/             # (Optional) for custom textures/images
```

**Note:** The entire application is self-contained in a single HTML file, making deployment extremely simple.

---

## Deployment to Google Cloud

### Option 1: Google Cloud Storage (Static Hosting)

#### Step 1: Create a Storage Bucket
```bash
# Install Google Cloud SDK if not already installed
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Create a new bucket (replace YOUR-BUCKET-NAME)
gsutil mb gs://YOUR-BUCKET-NAME

# Make bucket public for website hosting
gsutil iam ch allUsers:objectViewer gs://YOUR-BUCKET-NAME
```

#### Step 2: Configure Bucket for Web Hosting
```bash
# Set main page
gsutil web set -m index.html gs://YOUR-BUCKET-NAME

# Set error page (optional)
gsutil web set -e 404.html gs://YOUR-BUCKET-NAME
```

#### Step 3: Upload Your Files
```bash
# Upload the HTML file
gsutil cp index.html gs://YOUR-BUCKET-NAME/

# Set cache control (optional, for better performance)
gsutil setmeta -h "Cache-Control:public, max-age=3600" gs://YOUR-BUCKET-NAME/index.html
```

#### Step 4: Access Your Site
Your site will be available at:
```
https://storage.googleapis.com/YOUR-BUCKET-NAME/index.html
```

### Option 2: Google App Engine

#### Step 1: Create app.yaml
```yaml
runtime: python39
handlers:
  - url: /
    static_files: index.html
    upload: index.html
  - url: /(.*)
    static_files: \1
    upload: (.*)
```

#### Step 2: Deploy
```bash
gcloud app deploy
```

### Option 3: Firebase Hosting (Easiest)

#### Step 1: Install Firebase CLI
```bash
npm install -g firebase-tools
firebase login
```

#### Step 2: Initialize Project
```bash
firebase init hosting

# Select:
# - Use existing project or create new one
# - Set public directory to current directory (.)
# - Configure as single-page app: No
# - Set up automatic builds: No
```

#### Step 3: Deploy
```bash
firebase deploy --only hosting
```

---

## Customizing the UI

### 1. Changing Colors

#### Background Colors
```css
/* Located in <style> section */

/* Main background gradient */
body {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

/* 3D scene background */
scene.background = new THREE.Color(0x1a1a2e);  /* Dark blue */
```

#### Panel Colors
```css
/* Panel background */
#unified-panel {
    background: rgba(22, 33, 62, 0.95);  /* Semi-transparent dark blue */
}

/* Accent color (headings, active states) */
h2 {
    color: #f0ad4e;  /* Golden orange */
}
```

#### Button Colors
```css
/* Primary button gradient */
button.control-btn {
    background: linear-gradient(135deg, #5e72e4 0%, #825ee4 100%);
}

/* Active/selected button */
button.control-btn.active {
    background: linear-gradient(135deg, #f0ad4e 0%, #e89b3c 100%);
}
```

### 2. Modifying Panel Layout

#### Change Panel Position
```css
/* Currently at bottom center */
#unified-panel {
    bottom: 20px;           /* Distance from bottom */
    left: 50%;              /* Centered horizontally */
    transform: translateX(-50%);
}

/* To move to top center: */
#unified-panel {
    top: 20px;
    bottom: auto;
    left: 50%;
    transform: translateX(-50%);
}

/* To move to right side: */
#unified-panel {
    right: 20px;
    left: auto;
    bottom: 20px;
    transform: none;
}
```

#### Adjust Panel Size
```css
#unified-panel {
    max-width: 90%;         /* Maximum width on mobile */
    width: auto;            /* Auto-size to content */
}

/* Make panel wider: */
#unified-panel {
    max-width: 95%;
    min-width: 500px;       /* Minimum width on desktop */
}
```

#### Change Tab Layout
```css
/* Currently horizontal tabs */
.tab-container {
    display: flex;
    flex-direction: row;    /* Horizontal */
}

/* Make tabs vertical: */
.tab-container {
    display: flex;
    flex-direction: column; /* Vertical */
}
```

### 3. Adding New Tabs

#### Step 1: Add Tab Button (HTML)
```html
<div class="tab-container">
    <button class="tab-btn active" onclick="switchTab('info')">Info</button>
    <button class="tab-btn" onclick="switchTab('controls')">Controls</button>
    <button class="tab-btn" onclick="switchTab('views')">Views</button>
    
    <!-- ADD NEW TAB HERE -->
    <button class="tab-btn" onclick="switchTab('history')">History</button>
</div>
```

#### Step 2: Add Tab Content (HTML)
```html
<!-- ADD NEW CONTENT SECTION -->
<div id="history-tab" class="tab-content">
    <h2>Historical Context</h2>
    <p>The Treasury of Atreus was built around 1250 BCE...</p>
    <p>Add your content here!</p>
</div>
```

### 4. Modifying Text Content

All text content is in the HTML section. Search for these IDs:

```html
<!-- Info Panel -->
<div id="info-tab" class="tab-content active">
    <h2>Treasury of Atreus</h2>  <!-- Main title -->
    <p>c. 1250 BCE, Mycenae, Greece</p>  <!-- Subtitle -->
    
    <!-- Statistics - modify these -->
    <div class="stat">
        <span class="stat-label">Dome Diameter:</span>
        <span class="stat-value">14.5 m</span>
    </div>
</div>
```

### 5. Adding Custom Buttons

#### Example: Add a "Reset View" Button

**HTML (in controls-tab):**
```html
<div class="controls-grid">
    <!-- Existing buttons -->
    <button class="control-btn active" id="toggle-mound-btn">Earth Mound: ON</button>
    
    <!-- NEW BUTTON -->
    <button class="control-btn" id="reset-view-btn">Reset View</button>
</div>
```

**JavaScript:**
```javascript
document.getElementById('reset-view-btn').addEventListener('click', function() {
    // Reset camera to default position
    camera.position.set(40, 20, 40);
    controls.target.set(0, 6, 0);
    controls.update();
    
    // Optional: Show all elements
    earthMoundGroup.visible = true;
    rosettesGroup.visible = true;
    sideChamberGroup.visible = false;
});
```

---

## Modifying the 3D Model

### 1. Understanding the Structure

The 3D model is organized into groups:

```javascript
structureGroup          // Parent group containing everything
├── domeGroup          // The corbelled dome (33 courses)
├── earthMoundGroup    // Earth covering
├── rosettesGroup      // Bronze decorative rosettes
└── sideChamberGroup   // Rectangular burial chamber
```

### 2. Changing Stone Colors

```javascript
// Located in "MATERIALS" section

// Exterior stones (darker)
const stoneMaterial = new THREE.MeshStandardMaterial({
    color: 0xa89478,      // Hex color (beige/tan)
    roughness: 0.85,      // 0 = shiny, 1 = rough
    metalness: 0.1        // 0 = non-metal, 1 = metallic
});

// Interior stones (lighter)
const interiorStoneMaterial = new THREE.MeshStandardMaterial({
    color: 0xb5a08a,      // Lighter beige
    roughness: 0.7,
    metalness: 0.15
});

// Earth mound
const earthMaterial = new THREE.MeshStandardMaterial({
    color: 0x6b5d4f,      // Brown
    roughness: 0.95,
    metalness: 0.05
});
```

**Color Reference:**
- Use hex colors: `0xRRGGBB`
- Example: `0xff0000` = red, `0x00ff00` = green, `0x0000ff` = blue
- Use color pickers to find hex values

### 3. Adjusting Dimensions

All measurements are in meters and based on archaeological data:

```javascript
// Main dome dimensions
const domeDiameter = 14.5;  // 14.5 meters diameter
const domeHeight = 13.2;    // 13.2 meters tall
const numCourses = 33;      // 33 stone courses
const baseRadius = domeDiameter / 2;

// Dromos (entrance passage)
const dromosLength = 36;    // 36 meters long
const dromosWidth = 6;      // 6 meters wide
const dromosHeight = 5.4;   // 5.4 meters tall

// Entrance doorway
const doorwayHeight = 5.4;
const doorwayWidth = 2.7;
```

**To scale the entire structure:**
```javascript
// Add this after building the structure
structureGroup.scale.set(1.5, 1.5, 1.5);  // 150% size
structureGroup.scale.set(0.5, 0.5, 0.5);  // 50% size
```

### 4. Changing Lighting

#### Adjust Sun Light
```javascript
const sunLight = new THREE.DirectionalLight(0xffd8a8, 1.2);
//                                          ^^^^^^^^  ^^^
//                                          Color     Intensity

sunLight.position.set(30, 40, 30);  // X, Y, Z position
```

#### Add New Lights
```javascript
// Add a blue ambient light
const blueLight = new THREE.AmbientLight(0x4488ff, 0.3);
scene.add(blueLight);

// Add a spotlight
const spotlight = new THREE.SpotLight(0xffffff, 1.0);
spotlight.position.set(10, 20, 10);
spotlight.castShadow = true;
scene.add(spotlight);
```

### 5. Adding New 3D Elements

#### Example: Add a Flag on Top

```javascript
// Add this after the capstone section

// Flag pole
const poleGeometry = new THREE.CylinderGeometry(0.1, 0.1, 3, 8);
const poleMaterial = new THREE.MeshStandardMaterial({ color: 0x8b7355 });
const pole = new THREE.Mesh(poleGeometry, poleMaterial);
pole.position.set(0, domeHeight + 1.5, 0);
pole.castShadow = true;
structureGroup.add(pole);

// Flag
const flagGeometry = new THREE.PlaneGeometry(2, 1);
const flagMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xff0000,
    side: THREE.DoubleSide 
});
const flag = new THREE.Mesh(flagGeometry, flagMaterial);
flag.position.set(1, domeHeight + 2.5, 0);
structureGroup.add(flag);
```

### 6. Modifying Camera Views

Camera views are defined in the `setView()` function:

```javascript
window.setView = function(viewType) {
    switch(viewType) {
        case 'exterior':
            camera.position.set(40, 20, 40);    // X, Y, Z
            controls.target.set(0, 6, 0);       // Look at point
            break;
            
        // Add custom view
        case 'aerial':
            camera.position.set(0, 100, 0);     // Directly above
            controls.target.set(0, 0, 0);       // Look at center
            break;
    }
    controls.update();
};
```

---

## Troubleshooting

### Issue: Model Not Loading

**Check Console for Errors:**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for error messages

**Common fixes:**
- Ensure Three.js CDN is accessible
- Check that importmap is correctly formatted
- Verify no syntax errors in JavaScript

### Issue: Controls Not Working on Mobile

**Solutions:**
1. Ensure viewport meta tag is present:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

2. Test touch events:
```javascript
// Add touch event logging
renderer.domElement.addEventListener('touchstart', function(e) {
    console.log('Touch detected:', e.touches.length, 'fingers');
});
```

### Issue: Panel Buttons Too Small on Mobile

**Increase touch target size:**
```css
@media (max-width: 600px) {
    button.control-btn {
        padding: 16px;          /* Larger padding */
        font-size: 1rem;        /* Bigger text */
        min-height: 48px;       /* Minimum touch target */
    }
}
```

### Issue: Performance Problems

**Optimization tips:**

1. **Reduce stone count:**
```javascript
// In the dome building loop
const numBlocks = Math.max(6, Math.floor(currentRadius * 6)); // Reduced from 8
```

2. **Disable shadows on mobile:**
```javascript
// Check if mobile device
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

if (isMobile) {
    renderer.shadowMap.enabled = false;
}
```

3. **Lower renderer resolution:**
```javascript
// Render at 75% resolution on mobile
const pixelRatio = isMobile ? 0.75 : window.devicePixelRatio;
renderer.setPixelRatio(pixelRatio);
```

### Issue: Text Too Small/Large

**Adjust font sizes:**
```css
/* Base font sizes */
h1, h2 {
    font-size: 1.3rem;  /* Adjust as needed */
}

p {
    font-size: 0.9rem;
}

/* Mobile overrides */
@media (max-width: 600px) {
    h2 {
        font-size: 1.1rem;
    }
    p {
        font-size: 0.85rem;
    }
}
```

---

## Performance Optimization

### Enable Compression on Google Cloud

```bash
# Set gzip compression for HTML
gsutil setmeta -h "Content-Encoding:gzip" \
               -h "Content-Type:text/html" \
               gs://YOUR-BUCKET-NAME/index.html
```

### Add Loading Indicator

The model already includes a loading screen, but you can customize it:

```html
<div id="loading">
    <div class="spinner"></div>
    <p>Building Treasury of Atreus...</p>
    <p class="progress">0%</p>
</div>
```

```javascript
// Update progress during model building
let buildProgress = 0;
const totalSteps = 6;

function updateProgress() {
    buildProgress++;
    const percent = Math.floor((buildProgress / totalSteps) * 100);
    document.querySelector('.progress').textContent = percent + '%';
}

// Call updateProgress() after each major section
```

---

## Advanced Customization

### Adding Texture Maps

```javascript
// Load texture
const textureLoader = new THREE.TextureLoader();
const stoneTexture = textureLoader.load('path/to/stone-texture.jpg');

// Apply to material
const stoneMaterial = new THREE.MeshStandardMaterial({
    map: stoneTexture,
    roughness: 0.85,
    metalness: 0.1
});
```

### Adding Annotations/Labels

```javascript
// Create HTML label
const label = document.createElement('div');
label.className = 'label-3d';
label.textContent = 'Entrance Lintel (120 tons)';
label.style.position = 'absolute';
document.body.appendChild(label);

// Update position in animation loop
function animate() {
    // Convert 3D position to screen coordinates
    const vector = new THREE.Vector3(0, doorwayHeight + 1, baseRadius);
    vector.project(camera);
    
    const x = (vector.x * 0.5 + 0.5) * window.innerWidth;
    const y = (vector.y * -0.5 + 0.5) * window.innerHeight;
    
    label.style.left = x + 'px';
    label.style.top = y + 'px';
    
    // Rest of animation code...
}
```

### Adding Measurement Tools

```javascript
// Add distance measurement
function measureDistance(point1, point2) {
    const distance = point1.distanceTo(point2);
    console.log('Distance:', distance.toFixed(2), 'meters');
    
    // Draw line
    const geometry = new THREE.BufferGeometry().setFromPoints([point1, point2]);
    const material = new THREE.LineBasicMaterial({ color: 0xff0000 });
    const line = new THREE.Line(geometry, material);
    scene.add(line);
}
```

---

## Additional Resources

- **Three.js Documentation:** https://threejs.org/docs/
- **Three.js Examples:** https://threejs.org/examples/
- **Google Cloud Storage Docs:** https://cloud.google.com/storage/docs/hosting-static-website
- **Firebase Hosting Docs:** https://firebase.google.com/docs/hosting

---

## Support & Contact

For issues or questions:
1. Check the Troubleshooting section above
2. Review Three.js documentation
3. Check browser console for error messages
4. Test in different browsers (Chrome, Firefox, Safari)

**Browser Compatibility:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile Safari (iOS 14+)
- Chrome Mobile (Android 10+)

---

## License & Credits

This 3D model is based on archaeological data from:
- The Treasury of Atreus, Mycenae, Greece (c. 1250 BCE)
- Archaeological measurements and research
- Three.js library (MIT License)

Feel free to modify and use this code for educational or personal projects.