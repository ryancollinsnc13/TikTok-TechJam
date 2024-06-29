"use client"

import Image from "next/image";
import MainLayout from "./layouts/MainLayout"
import ClientOnly from "./components/ClientOnly";
import PostMain from "./components/PostMain";

export default function Home() {
  return (
    <>
      <MainLayout>
        <div className="mt-[80px]  w-[calc(100%-90px)] max-w-[690px] ml-auto">
          <ClientOnly>
              <PostMain post={{
                id:'123',
                user_id: '456',
                video_url: '/dog.mp4',
                text: 'temp text',
                created_at: 'date',
                profile: {
                  user_id:'456',
                  name:'Random user',
                  image: 'https://placehold.co/100'
                }
              }} />
          </ClientOnly>
        </div>
      </MainLayout>
    </>
  );
}
