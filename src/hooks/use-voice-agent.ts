
import { useConversation } from '@elevenlabs/react';
import { useState, useCallback } from 'react';

export const useVoiceAgent = () => {
  const conversation = useConversation();
  const [agentId, setAgentId] = useState<string>(() => {
    return localStorage.getItem('ELEVEN_LABS_AGENT_ID') || '';
  });

  const updateAgentId = useCallback((id: string) => {
    setAgentId(id);
    localStorage.setItem('ELEVEN_LABS_AGENT_ID', id);
  }, []);

  const startConversation = useCallback(async () => {
    if (!agentId) {
      throw new Error('Agent ID is required');
    }

    try {
      console.log('[useVoiceAgent] Starting conversation with Agent ID:', agentId);
      await conversation.startSession({
        agentId: agentId,
        // connectionType: 'websocket', // Optional, defaults to websocket if not specified
      });
    } catch (error) {
      console.error('Failed to start conversation:', error);
      throw error;
    }
  }, [agentId, conversation]);

  const stopConversation = useCallback(async () => {
    await conversation.endSession();
  }, [conversation]);

  return {
    status: conversation.status,
    isSpeaking: conversation.isSpeaking,
    startConversation,
    stopConversation,
    agentId,
    updateAgentId,
  };
};
