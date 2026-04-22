"use client";

import { useEffect, useRef } from "react";

/**
 * Lightweight canvas-based confetti burst.
 * - Gold/amber/stone palette to match the editorial design
 * - Respects `prefers-reduced-motion` automatically
 * - Self-cleans after animation completes
 * - No third-party dependencies
 */

const COLORS = [
  "#92400e", // amber-800
  "#b45309", // amber-700
  "#d4a574", // warm gold
  "#78716c", // stone-500
  "#a8a29e", // stone-400
  "#c2b8a3", // warm neutral
];

const PARTICLE_COUNT = 30;
const DURATION_MS = 2000;

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  color: string;
  alpha: number;
  decay: number;
  rotation: number;
  rotationSpeed: number;
  shape: "circle" | "rect";
}

export function ConfettiBurst() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    // Respect reduced motion preference
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (mq.matches) return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const parent = canvas.parentElement;
    if (!parent) return;
    const rect = parent.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    // Burst origin: center-top of the card
    const cx = canvas.width / 2;
    const cy = canvas.height * 0.15;

    const particles: Particle[] = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const angle =
        (Math.PI * 2 * i) / PARTICLE_COUNT + (Math.random() - 0.5) * 0.6;
      const speed = 1.2 + Math.random() * 3.5;
      particles.push({
        x: cx,
        y: cy,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 1.8,
        size: 2 + Math.random() * 3.5,
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
        alpha: 0.7 + Math.random() * 0.3,
        decay: 0.008 + Math.random() * 0.006,
        rotation: Math.random() * Math.PI * 2,
        rotationSpeed: (Math.random() - 0.5) * 0.1,
        shape: Math.random() > 0.5 ? "circle" : "rect",
      });
    }

    let animId: number;
    const start = performance.now();

    function animate(now: number) {
      const elapsed = now - start;
      if (elapsed > DURATION_MS) {
        ctx!.clearRect(0, 0, canvas!.width, canvas!.height);
        return;
      }

      ctx!.clearRect(0, 0, canvas!.width, canvas!.height);

      for (const p of particles) {
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.05; // gentle gravity
        p.alpha -= p.decay;
        p.rotation += p.rotationSpeed;

        if (p.alpha <= 0) continue;

        ctx!.save();
        ctx!.globalAlpha = Math.max(0, p.alpha);
        ctx!.fillStyle = p.color;
        ctx!.translate(p.x, p.y);
        ctx!.rotate(p.rotation);

        if (p.shape === "circle") {
          ctx!.beginPath();
          ctx!.arc(0, 0, p.size, 0, Math.PI * 2);
          ctx!.fill();
        } else {
          ctx!.fillRect(-p.size, -p.size * 0.5, p.size * 2, p.size);
        }

        ctx!.restore();
      }

      animId = requestAnimationFrame(animate);
    }

    animId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animId);
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute inset-0"
      aria-hidden="true"
    />
  );
}
