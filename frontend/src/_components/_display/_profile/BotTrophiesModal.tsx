import React from "react";
import Image from "next/image";

import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import Modal from "../Modal";
import MainButton from "@/_components/_props/MainButton";
// import { ProfileBotProps } from "../ProfileBot";
import { Bot } from "@/_components/_display/ProfileBotOverviewList";

interface TrophiesModalProps {
  bot: Bot;
  isOpen: boolean;
  onClose: () => void;
}

export default function TrophiesModal({ bot, isOpen, onClose }: TrophiesModalProps) {
  if (!isOpen) return null;

  return (
    <Modal onClose={onClose} title={`${bot.name}'s Trophies`}>
      <div className="p-4">
        {bot.trophies && bot.trophies.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {bot.trophies.map((trophy, index) => (
              <div
                key={index}
                className="flex flex-col items-center bg-gray-800 p-3 border border-gray-600 rounded-md"
              >
                <div className="w-12 h-12 relative mb-2">
                  <Image
                    src={`${getPublicPrefix()}/demo_assets/${trophy.image}`}
                    alt={trophy.title}
                    fill
                    style={{ objectFit: "contain" }}
                  />
                </div>
                <p className="text-xs text-gray-300 text-center">{trophy.title}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center">
            <p className="text-sm text-gray-400 mb-4">
              No trophies yet. Compete in competitions to earn trophies.
            </p>
            <MainButton text="Join Competition" href="hi" />
          </div>
        )}
      </div>
    </Modal>
  );
}
