<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Component\HttpFoundation\JsonResponse;
use App\Service\ApiService;
use App\Service\ConfigurationService;
use Psr\Log\LoggerInterface;

class ChatController extends AbstractController
{
    private ApiService $apiService;
    private ConfigurationService $config;
    private LoggerInterface $logger;

    public function __construct(
        ApiService $apiService,
        ConfigurationService $config,
        LoggerInterface $logger
    ) {
        $this->apiService = $apiService;
        $this->config = $config;
        $this->logger = $logger;
    }

    private function addCorsHeaders(array $headers = []): array
    {
        $corsConfig = $this->config->getCors();
        
        return array_merge($headers, [
            'Access-Control-Allow-Origin' => '*',
            'Access-Control-Allow-Methods' => implode(', ', $corsConfig['allowed_methods']),
            'Access-Control-Allow-Headers' => implode(', ', $corsConfig['allowed_headers']),
        ]);
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

    #[Route('/chat', name: 'chat_home', methods: ['GET', 'POST', 'OPTIONS'])]
    public function chatHome(Request $request): Response
    {
        // Handle preflight OPTIONS request
        if ($request->getMethod() === 'OPTIONS') {
            return new Response('', 200, $this->addCorsHeaders());
        }
        
        // Handle POST request (fallback for chat)
        if ($request->getMethod() === 'POST') {
            return $this->chatMessage($request);
        }
        
        return $this->render('chat/index.html.twig', [
            'mostRecentConversationId' => null,
            'currentConversationId' => null,
            'agent' => 'layla',
            'conversations' => [],
            'conversationsToday' => [],
            'conversationsYesterday' => [],
            'conversationsPrevious' => [],
            'today' => new \DateTime(),
            'user_id' => 1
        ]);
    }

    #[Route('/status', name: 'status_page')]
    public function status(): Response
    {
        return $this->render('status.html.twig');
    }

    #[Route('/chat/message', name: 'chat_message', methods: ['POST', 'OPTIONS'])]
    public function chatMessage(Request $request): JsonResponse
    {
        // Handle preflight OPTIONS request
        if ($request->getMethod() === 'OPTIONS') {
            return new JsonResponse('', 200, $this->addCorsHeaders());
        }
        
        try {
            $data = json_decode($request->getContent(), true);
            $userInput = $data['message'] ?? '';
            $conversationId = $data['conversation_id'] ?? null;
            $userId = $data['user_id'] ?? '1';

            $this->logger->info('Sending message to travel agent', [
                'conversation_id' => $conversationId,
                'user_input' => $userInput
            ]);

            $responseData = $this->apiService->sendChatMessage($userInput, $conversationId, $userId);
            
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

    #[Route('/chat/stream', name: 'chat_stream', methods: ['POST', 'OPTIONS'])]
    public function chatStream(Request $request): Response
    {
        // Handle preflight OPTIONS request
        if ($request->getMethod() === 'OPTIONS') {
            return new Response('', 200, $this->addCorsHeaders());
        }
        
        try {
            $data = json_decode($request->getContent(), true);
            $userInput = $data['message'] ?? '';
            $conversationId = $data['conversation_id'] ?? null;
            $userId = $data['user_id'] ?? '1';

            $this->logger->info('Sending streaming message to travel agent', [
                'conversation_id' => $conversationId,
                'user_input' => $userInput
            ]);

            return $this->apiService->getChatStream($userInput, $conversationId, $userId);

        } catch (\Exception $e) {
            $this->logger->error('Error in streaming chat', [
                'error' => $e->getMessage()
            ]);

            return new Response(
                "data: " . json_encode(['type' => 'error', 'error' => $e->getMessage()]) . "\n\n",
                500,
                $this->addCorsHeaders([
                    'Content-Type' => 'text/event-stream',
                ])
            );
        }
    }

    #[Route('/chat/status', name: 'chat_status', methods: ['GET'])]
    public function getAgentStatus(): JsonResponse
    {
        try {
            $statusData = $this->apiService->getStatus();
            
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
            $preferencesData = $this->apiService->getPreferences();
            
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

            $responseData = $this->apiService->updatePreference($key, $value);
            
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
            $responseData = $this->apiService->clearPreferences();
            
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

    #[Route('/chat/memory/clear', name: 'chat_memory_clear', methods: ['POST', 'OPTIONS'])]
    public function clearMemory(Request $request): JsonResponse
    {
        // Handle preflight OPTIONS request
        if ($request->getMethod() === 'OPTIONS') {
            return new JsonResponse('', 200, $this->addCorsHeaders());
        }
        
        try {
            // Get request body and forward it to Python API
            $requestBody = $request->getContent();
            $requestData = json_decode($requestBody, true) ?: [];
            
            $this->logger->info('Clearing memory', [
                'request_data' => $requestData
            ]);

            $conversationId = $requestData['conversation_id'] ?? null;
            $responseData = $this->apiService->clearMemory($conversationId);
            
            return new JsonResponse([
                'status' => 'success',
                'message' => $responseData['message'] ?? 'Mémoire de conversation effacée'
            ], 200, $this->addCorsHeaders());

        } catch (\Exception $e) {
            $this->logger->error('Error clearing memory', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return new JsonResponse([
                'status' => 'error',
                'message' => 'Impossible d\'effacer la mémoire de conversation',
                'error' => $e->getMessage()
            ], 500, $this->addCorsHeaders());
        }
    }

    #[Route('/chat/welcome', name: 'chat_welcome', methods: ['GET'])]
    public function getWelcomeMessage(): JsonResponse
    {
        try {
            $responseData = $this->apiService->getWelcomeMessage();
            
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

    #[Route('/api/config', name: 'api_config', methods: ['GET'])]
    public function getConfiguration(): JsonResponse
    {
        try {
            $config = $this->config->getAll();
            
            return new JsonResponse($config, 200, $this->addCorsHeaders());

        } catch (\Exception $e) {
            $this->logger->error('Error getting configuration', [
                'error' => $e->getMessage()
            ]);

            return new JsonResponse([
                'status' => 'error',
                'message' => 'Impossible de récupérer la configuration',
                'error' => $e->getMessage()
            ], 500, $this->addCorsHeaders());
        }
    }

}
