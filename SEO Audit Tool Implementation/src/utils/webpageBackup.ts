import { saveAs } from 'file-saver';

interface Asset {
  url: string;
  type: string;
  content: string;
}

export async function backupWebpage(url: string): Promise<void> {
  try {
    // Fetch the main HTML content
    const response = await fetch(url);
    const html = await response.text();
    
    // Create a DOM parser to analyze the HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    
    // Collect all assets (CSS, JS, images)
    const assets: Asset[] = [];
    
    // Process stylesheets
    const styleLinks = Array.from(doc.querySelectorAll('link[rel="stylesheet"]'));
    for (const link of styleLinks) {
      const cssUrl = new URL(link.getAttribute('href') || '', url).href;
      const cssResponse = await fetch(cssUrl);
      const cssContent = await cssResponse.text();
      assets.push({ url: cssUrl, type: 'css', content: cssContent });
      
      // Update the link href to use the local path
      link.setAttribute('href', `assets/${encodeURIComponent(cssUrl)}.css`);
    }
    
    // Process scripts
    const scripts = Array.from(doc.querySelectorAll('script[src]'));
    for (const script of scripts) {
      const scriptUrl = new URL(script.getAttribute('src') || '', url).href;
      const scriptResponse = await fetch(scriptUrl);
      const scriptContent = await scriptResponse.text();
      assets.push({ url: scriptUrl, type: 'js', content: scriptContent });
      
      // Update the script src to use the local path
      script.setAttribute('src', `assets/${encodeURIComponent(scriptUrl)}.js`);
    }
    
    // Process images
    const images = Array.from(doc.querySelectorAll('img'));
    for (const img of images) {
      const imgUrl = new URL(img.getAttribute('src') || '', url).href;
      const imgResponse = await fetch(imgUrl);
      const imgBlob = await imgResponse.blob();
      const imgContent = await blobToBase64(imgBlob);
      assets.push({ url: imgUrl, type: 'image', content: imgContent });
      
      // Update the image src to use the local path
      img.setAttribute('src', `assets/${encodeURIComponent(imgUrl)}`);
    }
    
    // Create a zip file containing all assets
    const zip = new JSZip();
    
    // Add the modified HTML
    zip.file('index.html', doc.documentElement.outerHTML);
    
    // Create assets folder
    const assetsFolder = zip.folder('assets');
    if (assetsFolder) {
      // Add all assets to the zip
      assets.forEach(asset => {
        const filename = encodeURIComponent(asset.url) + (asset.type === 'image' ? '' : '.' + asset.type);
        assetsFolder.file(filename, asset.content);
      });
    }
    
    // Generate and download the zip file
    const zipBlob = await zip.generateAsync({ type: 'blob' });
    const domain = new URL(url).hostname;
    saveAs(zipBlob, `${domain}-backup.zip`);
    
  } catch (error) {
    console.error('Error creating backup:', error);
    throw new Error('Failed to create webpage backup');
  }
}

function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}