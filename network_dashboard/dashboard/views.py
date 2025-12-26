from django.shortcuts import render
from datetime import datetime


def index(request):
    alerts = [
        {
            'title': 'Queda de link - Matriz',
            'severity': 'high',
            'timestamp': datetime(2024, 8, 15, 10, 32),
            'description': 'Link primário indisponível. Tráfego migrado para backup.',
        },
        {
            'title': 'Firewall - Tentativa de intrusão',
            'severity': 'medium',
            'timestamp': datetime(2024, 8, 15, 9, 58),
            'description': 'Bloqueio automático aplicado no perímetro leste.',
        },
        {
            'title': 'Janela de manutenção - Data center',
            'severity': 'low',
            'timestamp': datetime(2024, 8, 16, 1, 0),
            'description': 'Atualização de firmware em switches core.',
        },
    ]

    manuals = [
        {
            'category': 'Switches',
            'items': [
                {'title': 'POP - Backup de configuração', 'format': 'pdf'},
                {'title': 'Checklist pós-upgrade', 'format': 'md'},
            ],
        },
        {
            'category': 'Roteadores',
            'items': [
                {'title': 'Procedimento de failover BGP', 'format': 'md'},
                {'title': 'Template de baseline', 'format': 'pdf'},
            ],
        },
        {
            'category': 'Servidores',
            'items': [
                {'title': 'Hardening Linux', 'format': 'md'},
                {'title': 'Checklist de patches', 'format': 'pdf'},
            ],
        },
        {
            'category': 'VPN',
            'items': [
                {'title': 'Onboarding de usuários', 'format': 'md'},
                {'title': 'Runbook de contingência', 'format': 'pdf'},
            ],
        },
    ]

    tasks = [
        {'title': 'Conferir backups', 'key': 'backup'},
        {'title': 'Verificar logs críticos', 'key': 'logs'},
        {'title': 'Monitorar banda WAN', 'key': 'bandwidth'},
        {'title': 'Aplicar patches de segurança', 'key': 'patching'},
    ]

    context = {
        'alerts': alerts,
        'manuals': manuals,
        'tasks': tasks,
    }
    return render(request, 'dashboard/index.html', context)
