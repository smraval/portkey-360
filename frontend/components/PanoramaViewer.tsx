"use client";
import { Canvas, useLoader, useThree } from '@react-three/fiber';
import { TextureLoader, DoubleSide, Vector3 } from 'three';
import { OrbitControls, Html } from '@react-three/drei';
import { Suspense, useEffect } from 'react';
import * as THREE from 'three';

interface Props {
  src: string;
  isLoading?: boolean;
}

function Sphere({ src }: { src: string }) {
  const texture = useLoader(TextureLoader, src);

  return (
    <mesh scale={[-1, 1, 1]}>
      <sphereGeometry args={[500, 32, 16]} />
      <meshBasicMaterial 
        map={texture} 
        side={DoubleSide}
      />
    </mesh>
  );
}

function LoadingFallback() {
  return (
    <Html center>
      <div className="text-gray-600 text-center">
        <div className="w-8 h-8 border-2 border-gray-400 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
        <p>Loading panorama...</p>
      </div>
    </Html>
  );
}

function CameraController() {
  const { camera } = useThree();
  
  useEffect(() => {
    camera.position.set(0, 0, 0.1);
    camera.lookAt(new Vector3(0, 0, 0));
  }, [camera]);

  return null;
}

export default function PanoramaViewer({ src, isLoading }: Props) {
  if (!src) return null;

  return (
    <Canvas 
      camera={{ 
        fov: 75, 
        position: [0, 0, 0.1],
        near: 0.1,
        far: 1000
      }}
      gl={{ 
        antialias: true,
        alpha: false,
        powerPreference: "high-performance"
      }}
    >
      <CameraController />
      
      <Suspense fallback={<LoadingFallback />}>
      <Sphere src={src} />
      </Suspense>
      
      <OrbitControls 
        enableZoom={true}
        enablePan={false}
        enableDamping={true}
        dampingFactor={0.05}
        rotateSpeed={0.5}
        minDistance={0.1}
        maxDistance={1000}
        maxPolarAngle={Math.PI}
        minPolarAngle={0}
        target={[0, 0, 0]}
      />
    </Canvas>
  );
}
