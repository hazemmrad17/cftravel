<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Psr\Log\LoggerInterface;
use App\Service\ApiService;

#[Route('/api')]
class DashboardApiController extends AbstractController
{
    private $logger;
    private $apiService;

    public function __construct(LoggerInterface $logger, ApiService $apiService)
    {
        $this->logger = $logger;
        $this->apiService = $apiService;
    }

    #[Route('/settings/update', name: 'api_settings_update', methods: ['POST'])]
    public function updateSetting(Request $request): JsonResponse
    {
        try {
            $data = json_decode($request->getContent(), true);
            
            $this->logger->info('Dashboard setting update request', [
                'setting_id' => $data['setting_id'] ?? 'unknown',
                'value' => $data['value'] ?? null
            ]);

            // Forward to Python backend
            $response = $this->apiService->request('POST', 'settings/update', $data);
            
            return new JsonResponse($response);
            
        } catch (\Exception $e) {
            $this->logger->error('Error updating dashboard setting', [
                'error' => $e->getMessage()
            ]);
            
            return new JsonResponse([
                'success' => false,
                'message' => 'Error updating setting: ' . $e->getMessage()
            ], 500);
        }
    }

    #[Route('/settings/save', name: 'api_settings_save', methods: ['POST'])]
    public function saveSettings(Request $request): JsonResponse
    {
        try {
            $data = json_decode($request->getContent(), true);
            
            $this->logger->info('Dashboard settings save request', [
                'settings_count' => count($data['settings'] ?? []),
                'user_id' => $data['user_id'] ?? 'unknown'
            ]);

            // Forward to Python backend
            $response = $this->apiService->request('POST', 'settings/save', $data);
            
            return new JsonResponse($response);
            
        } catch (\Exception $e) {
            $this->logger->error('Error saving dashboard settings', [
                'error' => $e->getMessage()
            ]);
            
            return new JsonResponse([
                'success' => false,
                'message' => 'Error saving settings: ' . $e->getMessage()
            ], 500);
        }
    }

    #[Route('/settings/get', name: 'api_settings_get', methods: ['GET'])]
    public function getSettings(): JsonResponse
    {
        try {
            $this->logger->info('Dashboard settings get request');

            // Forward to Python backend
            $response = $this->apiService->request('GET', 'settings/get');
            
            return new JsonResponse($response);
            
        } catch (\Exception $e) {
            $this->logger->error('Error getting dashboard settings', [
                'error' => $e->getMessage()
            ]);
            
            return new JsonResponse([
                'success' => false,
                'message' => 'Error getting settings: ' . $e->getMessage()
            ], 500);
        }
    }

    #[Route('/cache/clear', name: 'api_cache_clear', methods: ['POST'])]
    public function clearCache(): JsonResponse
    {
        try {
            $this->logger->info('Dashboard cache clear request');

            // Forward to Python backend
            $response = $this->apiService->request('POST', 'cache/clear');
            
            return new JsonResponse($response);
            
        } catch (\Exception $e) {
            $this->logger->error('Error clearing cache', [
                'error' => $e->getMessage()
            ]);
            
            return new JsonResponse([
                'success' => false,
                'message' => 'Error clearing cache: ' . $e->getMessage()
            ], 500);
        }
    }

    #[Route('/stats/realtime', name: 'api_stats_realtime', methods: ['GET'])]
    public function getRealTimeStats(): JsonResponse
    {
        try {
            $this->logger->info('Dashboard real-time stats request');

            // Forward to Python backend
            $response = $this->apiService->request('GET', 'stats/realtime');
            
            return new JsonResponse($response);
            
        } catch (\Exception $e) {
            $this->logger->error('Error getting real-time stats', [
                'error' => $e->getMessage()
            ]);
            
            return new JsonResponse([
                'success' => false,
                'message' => 'Error getting stats: ' . $e->getMessage()
            ], 500);
        }
    }

    #[Route('/system/status', name: 'api_system_status', methods: ['GET'])]
    public function getSystemStatus(): JsonResponse
    {
        try {
            $this->logger->info('Dashboard system status request');

            // Forward to Python backend
            $response = $this->apiService->request('GET', 'system/status');
            
            return new JsonResponse($response);
            
        } catch (\Exception $e) {
            $this->logger->error('Error getting system status', [
                'error' => $e->getMessage()
            ]);
            
            return new JsonResponse([
                'success' => false,
                'message' => 'Error getting system status: ' . $e->getMessage()
            ], 500);
        }
    }
} 