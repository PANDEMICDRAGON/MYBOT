import { useRef, useState, useEffect } from 'react';
import Head from 'next/head';

const ClippingTool = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const [imageSrc, setImageSrc] = useState<string>('');
  const [isDrawing, setIsDrawing] = useState(false);
  const [startPos, setStartPos] = useState<{ x: number; y: number } | null>(null);
  const [rect, setRect] = useState<{ x: number; y: number; w: number; h: number } | null>(
    null
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setImageSrc(url);
  };

  // Draw image and selection rectangle
  const draw = () => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Draw image if loaded
    if (imgRef.current && imgRef.current.complete) {
      const img = imgRef.current;
      const scale = Math.min(
        canvas.width / img.width,
        canvas.height / img.height
      );
      const drawW = img.width * scale;
      const drawH = img.height * scale;
      ctx.drawImage(img, 0, 0, drawW, drawH);
      // Store scaled dimensions for later clipping
      (canvas as any)._scaled = { w: drawW, h: drawH, scale };
    }
    // Draw selection rectangle if present
    if (rect) {
      ctx.strokeStyle = 'red';
      ctx.lineWidth = 2;
      ctx.setLineDash([6, 4]);
      ctx.strokeRect(rect.x, rect.y, rect.w, rect.h);
    }
  };

  useEffect(() => {
    draw();
  }, [imageSrc, rect]);

  const getMousePos = (e: React.MouseEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    };
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!imageSrc) return;
    const pos = getMousePos(e);
    setStartPos(pos);
    setIsDrawing(true);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDrawing || !startPos) return;
    const pos = getMousePos(e);
    const newRect = {
      x: Math.min(startPos.x, pos.x),
      y: Math.min(startPos.y, pos.y),
      w: Math.abs(pos.x - startPos.x),
      h: Math.abs(pos.y - startPos.y),
    };
    setRect(newRect);
  };

  const handleMouseUp = () => {
    setIsDrawing(false);
    setStartPos(null);
  };

  const handleDownload = () => {
    if (!rect) return;
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;
    const { w: scaleW, h: scaleH, scale } = (canvas as any)._scaled || {};
    if (!scale) return;
    // Map rectangle back to original image coordinates
    const sx = rect.x / scale;
    const sy = rect.y / scale;
    const sw = rect.w / scale;
    const sh = rect.h / scale;
    // Create an off‑screen canvas for the clipped region
    const off = document.createElement('canvas');
    off.width = rect.w;
    off.height = rect.h;
    const offCtx = off.getContext('2d');
    if (!offCtx) return;
    const img = imgRef.current;
    if (!img) return;
    offCtx.drawImage(img, sx, sy, sw, sh, 0, 0, rect.w, rect.h);
    // Convert to blob and trigger download
    off.toBlob((blob) => {
      if (!blob) return;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'clipped.png';
      a.click();
      URL.revokeObjectURL(url);
    }, 'image/png');
  };

  return (
    <>
      <Head>
        <title>🛠️ Clipping Tool – Michael's Lab</title>
      </Head>
      <main className="flex flex-col items-center p-8 min-h-screen bg-gray-50">
        <h1 className="text-3xl font-bold mb-6">Clipping Tool 🎨</h1>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="mb-4"
        />
        <div className="relative border border-gray-300">
          <canvas
            ref={canvasRef}
            width={800}
            height={500}
            className="cursor-crosshair"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
          />
          {/* Hidden img element to keep the original source */}
          {imageSrc && (
            <img
              ref={imgRef}
              src={imageSrc}
              alt="uploaded"
              style={{ display: 'none' }}
            />
          )}
        </div>
        {rect && (
          <button
            onClick={handleDownload}
            className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          >
            Download Clip 📥
          </button>
        )}
      </main>
    </>
  );
};

export default ClippingTool;
