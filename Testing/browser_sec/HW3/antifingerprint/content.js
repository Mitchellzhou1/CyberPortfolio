(function () {
  const injectScript = function () {
    const script = document.createElement('script');
    script.textContent = `(${overrideCanvas.toString()})();`;
    document.documentElement.appendChild(script);
    script.remove();
  };

  const overrideCanvas = function () {
    const getRandomInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

    const addNoise = (canvas, ctx) => {
      const width = canvas.width;
      const height = canvas.height;
      const imageData = ctx.getImageData(0, 0, width, height);
      for (let i = 0; i < imageData.data.length; i += 4) {
        imageData.data[i]     = imageData.data[i]     + getRandomInt(-5, 5); // R
        imageData.data[i + 1] = imageData.data[i + 1] + getRandomInt(-5, 5); // G
        imageData.data[i + 2] = imageData.data[i + 2] + getRandomInt(-5, 5); // B
      }
      ctx.putImageData(imageData, 0, 0);
    };

    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function () {
      const ctx = this.getContext('2d');
      addNoise(this, ctx);
      return originalToDataURL.apply(this, arguments);
    };

    const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
    CanvasRenderingContext2D.prototype.getImageData = function () {
      const imageData = originalGetImageData.apply(this, arguments);
      for (let i = 0; i < imageData.data.length; i += 4) {
        imageData.data[i]     = imageData.data[i]     + getRandomInt(-5, 5);
        imageData.data[i + 1] = imageData.data[i + 1] + getRandomInt(-5, 5);
        imageData.data[i + 2] = imageData.data[i + 2] + getRandomInt(-5, 5);
      }
      return imageData;
    };
  };

  injectScript();
})();
