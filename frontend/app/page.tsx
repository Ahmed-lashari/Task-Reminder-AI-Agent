"use client";

import { useCallback } from "react";
import { IdentityGate } from "@/components/IdentityGate";
import { ProjectSidebar } from "@/components/ProjectSidebar";
import { TechStackSidebar } from "@/components/TechStackSidebar";
import { ChatPanel } from "@/components/ChatPanel";
import { useIdentity } from "@/hooks/useIdentity";
import { useChat } from "@/hooks/useChat";
import { useReminderSocket } from "@/hooks/useReminderSocket";

export default function Home() {
  const { identity, isLoaded, establishIdentity, clearIdentity } = useIdentity();

  return (
    <IdentityGuard
      isLoaded={isLoaded}
      identityOwnerId={identity?.ownerId ?? null}
      identityName={identity?.name ?? null}
      onEstablish={establishIdentity}
      onReset={clearIdentity}
    />
  );
}

interface IdentityGuardProps {
  isLoaded: boolean;
  identityOwnerId: string | null;
  identityName: string | null;
  onEstablish: (name: string, secret: string) => Promise<unknown>;
  onReset: () => void;
}

function IdentityGuard({ isLoaded, identityOwnerId, identityName, onEstablish, onReset }: IdentityGuardProps) {
  const handleSubmit = useCallback(
    async (name: string, secret: string) => {
      await onEstablish(name, secret);
    },
    [onEstablish]
  );

  if (!isLoaded) {
    return <div className="min-h-screen bg-base" />;
  }

  if (!identityOwnerId || !identityName) {
    return <IdentityGate onSubmit={handleSubmit} />;
  }

  return <Workspace ownerId={identityOwnerId} name={identityName} onReset={onReset} />;
}

function Workspace({ ownerId, name, onReset }: { ownerId: string; name: string; onReset: () => void }) {
  const { messages, isSending, error, send, receiveSystemMessage } = useChat(ownerId);
  useReminderSocket(ownerId, receiveSystemMessage);

  return (
    <div className="grid h-screen grid-cols-1 lg:grid-cols-[260px_1fr_260px]">
      <div className="order-2 lg:order-1">
        <ProjectSidebar name={name} onReset={onReset} />
      </div>
      <div className="order-1 h-[70vh] lg:order-2 lg:h-full">
        <ChatPanel messages={messages} isSending={isSending} error={error} onSend={send} />
      </div>
      <div className="order-3">
        <TechStackSidebar />
      </div>
    </div>
  );
}
