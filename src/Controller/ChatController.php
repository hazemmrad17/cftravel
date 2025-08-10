<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Contracts\HttpClient\HttpClientInterface;
use Psr\Log\LoggerInterface;

class ChatController extends AbstractController
{
    private HttpClientInterface $httpClient;
    private LoggerInterface $logger;
    private string $agentApiUrl;

    public function __construct(HttpClientInterface $httpClient, LoggerInterface $logger)
    {
        $this->httpClient = $httpClient;
        $this->logger = $logger;
        $this->agentApiUrl = $_ENV['AGENT_API_URL'] ?? 'http://localhost:8001';
    }

    #[Route('/', name: 'app_home')]
    public function index(): Response
    {
        return $this->render('chat/index.html.twig', [
            'mostRecentConversationId' => null,
            'currentConversationId' => null,
            'agent' => 'layla', // Changed to 'layla' for the travel agent
            'conversations' => [],
            'today' => new \DateTime()
        ]);
    }
    
    #[Route('/home', name: 'home_page')]
    public function home(): Response
    {
        return $this->render('home.html.twig');
    }

    #[Route('/conversation/new', name: 'create_conversation_route')]
    public function createConversation(): Response
    {
        // TODO: Implement conversation creation logic
        return $this->redirectToRoute('app_home');
    }

    #[Route('/settings', name: 'settings_page')]
    public function settings(): Response
    {
        return $this->render('settings.html.twig');
    }

    #[Route('/privacy', name: 'privacy_page')]
    public function privacy(): Response
    {
        return $this->render('privacy.html.twig');
    }

    #[Route('/pricing', name: 'pricing_page')]
    public function pricing(): Response
    {
        return $this->render('pricing.html.twig');
    }

    #[Route('/faq', name: 'faq_page')]
    public function faq(): Response
    {
        return $this->render('faq.html.twig');
    }

    #[Route('/contact', name: 'contact_page')]
    public function contact(): Response
    {
        return $this->render('contact.html.twig');
    }

    #[Route('/billing', name: 'billing_page')]
    public function billing(): Response
    {
        return $this->render('billing.html.twig');
    }

    #[Route('/chat', name: 'chat_home', methods: ['GET'])]
    public function chatHome(): Response
    {
        return $this->render('chat/chat.html.twig');
    }

    #[Route('/status', name: 'status_page')]
    public function status(): Response
    {
        return $this->render('status.html.twig');
    }

    #[Route('/chat/message', name: 'chat_message', methods: ['POST'])]
    public function chatMessage(Request $request): JsonResponse
    {
        try {
            $data = json_decode($request->getContent(), true);
            $userInput = $data['message'] ?? '';
            $conversationId = $data['conversation_id'] ?? null;
            $userId = $data['user_id'] ?? 1;

            $this->logger->info('Sending message to travel agent', [
                'conversation_id' => $conversationId,
                'user_input' => $userInput
            ]);

            $response = $this->httpClient->request('POST', $this->agentApiUrl . '/chat', [
                'json' => [
                    'message' => $userInput,
                    'conversation_id' => $conversationId,
                    'user_id' => $userId
                ],
                'timeout' => 30
            ]);

            $responseData = $response->toArray();
            
            $this->logger->info('Received response from travel agent', [
                'status' => $responseData['status'] ?? 'unknown'
            ]);

            return new JsonResponse($responseData);

        } catch (\Exception $e) {
            $this->logger->error('Error in chat message', [
                'error' => $e->getMessage()
            ]);

            return new JsonResponse([
                'status' => 'error',
                'response' => 'Désolé, je rencontre des difficultés techniques. Veuillez réessayer.',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    #[Route('/chat/stream', name: 'chat_stream', methods: ['POST'])]
    public function chatStream(Request $request): Response
    {
        try {
            $data = json_decode($request->getContent(), true);
            $userInput = $data['message'] ?? '';
            $conversationId = $data['conversation_id'] ?? null;
            $userId = $data['user_id'] ?? 1;

            $this->logger->info('Sending streaming message to travel agent', [
                'conversation_id' => $conversationId,
                'user_input' => $userInput
            ]);

            // Forward the streaming request to the Python API
            $response = $this->httpClient->request('POST', $this->agentApiUrl . '/chat/stream', [
                'json' => [
                    'message' => $userInput,
                    'conversation_id' => $conversationId,
                    'user_id' => $userId
                ],
                'timeout' => 60
            ]);

            // Return the streaming response
            return new Response(
                $response->getContent(),
                $response->getStatusCode(),
                [
                    'Content-Type' => 'text/event-stream',
                    'Cache-Control' => 'no-cache',
                    'Connection' => 'keep-alive',
                ]
            );

        } catch (\Exception $e) {
            $this->logger->error('Error in streaming chat', [
                'error' => $e->getMessage()
            ]);

            return new Response(
                "data: " . json_encode(['type' => 'error', 'error' => $e->getMessage()]) . "\n\n",
                500,
                ['Content-Type' => 'text/event-stream']
            );
        }
    }

    #[Route('/chat/status', name: 'chat_status', methods: ['GET'])]
    public function getAgentStatus(): JsonResponse
    {
        try {
            $response = $this->httpClient->request('GET', $this->agentApiUrl . '/status', [
                'timeout' => 10
            ]);

            $statusData = $response->toArray();
            
            return new JsonResponse([
                'status' => 'success',
                'agent_status' => $statusData
            ]);

        } catch (\Exception $e) {
            $this->logger->error('Error getting agent status', [
                'error' => $e->getMessage()
            ]);

            return new JsonResponse([
                'status' => 'error',
                'message' => 'Impossible de vérifier le statut de l\'agent',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    #[Route('/chat/preferences', name: 'chat_preferences', methods: ['GET'])]
    public function getPreferences(): JsonResponse
    {
        try {
            $response = $this->httpClient->request('GET', $this->agentApiUrl . '/preferences', [
                'timeout' => 10
            ]);

            $preferencesData = $response->toArray();
            
            return new JsonResponse([
                'status' => 'success',
                'preferences' => $preferencesData['preferences'] ?? []
            ]);

        } catch (\Exception $e) {
            $this->logger->error('Error getting preferences', [
                'error' => $e->getMessage()
            ]);

            return new JsonResponse([
                'status' => 'error',
                'message' => 'Impossible de récupérer les préférences',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    #[Route('/chat/preferences', name: 'update_preference', methods: ['POST'])]
    public function updatePreference(Request $request): JsonResponse
    {
        try {
            $data = json_decode($request->getContent(), true);
            $key = $data['key'] ?? '';
            $value = $data['value'] ?? '';

            if (empty($key) || empty($value)) {
                return new JsonResponse([
                    'status' => 'error',
                    'message' => 'Clé et valeur requises'
                ], 400);
            }

            $response = $this->httpClient->request('POST', $this->agentApiUrl . '/preferences', [
                'json' => [
                    'key' => $key,
                    'value' => $value
                ],
                'timeout' => 10
            ]);

            $responseData = $response->toArray();
            
            return new JsonResponse([
                'status' => 'success',
                'message' => $responseData['message'] ?? 'Préférence mise à jour'
            ]);

        } catch (\Exception $e) {
            $this->logger->error('Error updating preference', [
                'error' => $e->getMessage()
            ]);

            return new JsonResponse([
                'status' => 'error',
                'message' => 'Impossible de mettre à jour la préférence',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    #[Route('/chat/preferences', name: 'chat_preferences_delete', methods: ['DELETE'])]
    public function clearPreferences(): JsonResponse
    {
        try {
            $response = $this->httpClient->request('DELETE', $this->agentApiUrl . '/preferences', [
                'timeout' => 10
            ]);

            $responseData = $response->toArray();
            
            return new JsonResponse([
                'status' => 'success',
                'message' => $responseData['message'] ?? 'Préférences effacées'
            ]);

        } catch (\Exception $e) {
            $this->logger->error('Error clearing preferences', [
                'error' => $e->getMessage()
            ]);

            return new JsonResponse([
                'status' => 'error',
                'message' => 'Impossible d\'effacer les préférences',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    #[Route('/chat/memory/clear', name: 'chat_memory_clear', methods: ['POST'])]
    public function clearMemory(): JsonResponse
    {
        try {
            $response = $this->httpClient->request('POST', $this->agentApiUrl . '/memory/clear', [
                'timeout' => 10
            ]);

            $responseData = $response->toArray();
            
            return new JsonResponse([
                'status' => 'success',
                'message' => $responseData['message'] ?? 'Mémoire de conversation effacée'
            ]);

        } catch (\Exception $e) {
            $this->logger->error('Error clearing memory', [
                'error' => $e->getMessage()
            ]);

            return new JsonResponse([
                'status' => 'error',
                'message' => 'Impossible d\'effacer la mémoire de conversation',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    #[Route('/chat/welcome', name: 'chat_welcome', methods: ['GET'])]
    public function getWelcomeMessage(): JsonResponse
    {
        try {
            $response = $this->httpClient->request('GET', $this->agentApiUrl . '/welcome', [
                'timeout' => 10
            ]);

            $responseData = $response->toArray();
            
            return new JsonResponse([
                'status' => 'success',
                'message' => $responseData['message'] ?? 'Bonjour! Je suis Layla, votre agent de voyage personnel! 🧳✈️'
            ]);

        } catch (\Exception $e) {
            $this->logger->error('Error getting welcome message', [
                'error' => $e->getMessage()
            ]);

            return new JsonResponse([
                'status' => 'error',
                'message' => 'Bonjour! Je suis Layla, votre agent de voyage personnel! 🧳✈️',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}
