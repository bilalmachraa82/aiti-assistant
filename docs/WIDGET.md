# Guia do Widget - AITI Assistant

## Instalação Rápida

Adicione duas linhas ao seu website:

```html
<script src="https://seu-dominio.com/widget/aiti-widget.js"></script>
<script>
  AITIWidget.init({
    apiUrl: 'https://api.seu-dominio.com'
  });
</script>
```

Pronto! O widget aparece no canto inferior direito.

---

## Configuração Completa

```html
<script src="https://seu-dominio.com/widget/aiti-widget.js"></script>
<script>
  AITIWidget.init({
    // Obrigatório
    apiUrl: 'https://api.seu-dominio.com',
    
    // Opcional - Autenticação
    apiKey: 'sua-api-key-se-configurada',
    
    // Opcional - Aparência
    primaryColor: '#0066cc',
    textColor: '#ffffff',
    position: 'bottom-right',  // ou 'bottom-left'
    
    // Opcional - Textos
    title: 'Assistente Virtual',
    subtitle: 'Estamos aqui para ajudar',
    welcomeMessage: 'Olá! 👋 Como posso ajudar?',
    placeholder: 'Escreva a sua pergunta...',
    
    // Opcional - Branding
    showPoweredBy: true
  });
</script>
```

---

## Opções de Configuração

| Opção | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `apiUrl` | string | URL actual | URL do backend |
| `apiKey` | string | null | API key (se configurada) |
| `primaryColor` | string | `#0066cc` | Cor principal |
| `textColor` | string | `#ffffff` | Cor do texto nos botões |
| `position` | string | `bottom-right` | Posição do widget |
| `title` | string | `Assistente Virtual` | Título no header |
| `subtitle` | string | `Estamos aqui para ajudar` | Subtítulo no header |
| `welcomeMessage` | string | `Olá! 👋...` | Mensagem inicial |
| `placeholder` | string | `Escreva...` | Placeholder do input |
| `showPoweredBy` | boolean | true | Mostrar "Powered by" |

---

## Personalização de Cores

### Cor da Marca

```javascript
AITIWidget.init({
  apiUrl: 'https://api.empresa.pt',
  primaryColor: '#e74c3c',  // Vermelho
  textColor: '#ffffff'
});
```

### Cores Populares

| Estilo | primaryColor | Resultado |
|--------|--------------|-----------|
| Azul corporativo | `#0066cc` | Profissional |
| Verde natureza | `#27ae60` | Amigável |
| Roxo premium | `#9b59b6` | Sofisticado |
| Laranja energia | `#f39c12` | Dinâmico |
| Preto elegante | `#2c3e50` | Minimalista |

---

## API JavaScript

### Abrir/Fechar Programaticamente

```javascript
// Abrir o chat
AITIWidget.open();

// Fechar o chat
AITIWidget.close();
```

### Enviar Mensagem Programaticamente

```javascript
// Útil para botões de FAQ no site
AITIWidget.sendMessage('Qual o prazo de entrega?');
```

### Exemplo: Botões de Perguntas Rápidas

```html
<button onclick="perguntarEntrega()">📦 Prazos de Entrega</button>
<button onclick="perguntarDevolucao()">↩️ Devoluções</button>

<script>
function perguntarEntrega() {
  AITIWidget.open();
  setTimeout(() => {
    AITIWidget.sendMessage('Quais são os prazos de entrega?');
  }, 300);
}

function perguntarDevolucao() {
  AITIWidget.open();
  setTimeout(() => {
    AITIWidget.sendMessage('Como faço uma devolução?');
  }, 300);
}
</script>
```

---

## Integração com Analytics

### Google Analytics

```javascript
// Interceptar eventos do widget
window.addEventListener('aiti-message-sent', function(e) {
  gtag('event', 'chat_message', {
    'event_category': 'AITI Widget',
    'event_label': e.detail.query.substring(0, 50)
  });
});

window.addEventListener('aiti-chat-opened', function() {
  gtag('event', 'chat_opened', {
    'event_category': 'AITI Widget'
  });
});
```

---

## Responsividade

O widget adapta-se automaticamente a mobile:
- Em ecrãs <420px: ocupa quase toda a largura
- Botão sempre acessível no canto
- Input optimizado para touch

---

## Self-Hosting do Widget

Se preferir hospedar o widget localmente:

1. Copie `widget/aiti-widget.js` para o seu servidor
2. Atualize o `src` no script

```html
<script src="/assets/js/aiti-widget.js"></script>
```

---

## Troubleshooting

### Widget não aparece
- Verifique se o script está a carregar (DevTools > Network)
- Confirme que `AITIWidget.init()` é chamado
- Verifique erros na consola

### CORS Error
- Configure `CORS_ORIGINS` no backend:
```env
CORS_ORIGINS=https://seu-site.pt,https://www.seu-site.pt
```

### Respostas lentas
- Verifique latência ao backend
- Considere usar CDN para o widget.js

### Estilo conflitua com o site
- O widget usa classes com prefixo `aiti-` para evitar conflitos
- Se necessário, aumente especificidade no CSS

---

## Exemplos de Integração

### WordPress

```php
// No functions.php ou plugin
function add_aiti_widget() {
  ?>
  <script src="https://api.empresa.pt/widget/aiti-widget.js"></script>
  <script>
    AITIWidget.init({
      apiUrl: 'https://api.empresa.pt',
      primaryColor: '#0073aa'  // Cor do WordPress
    });
  </script>
  <?php
}
add_action('wp_footer', 'add_aiti_widget');
```

### Shopify

```liquid
<!-- No theme.liquid, antes de </body> -->
<script src="https://api.empresa.pt/widget/aiti-widget.js"></script>
<script>
  AITIWidget.init({
    apiUrl: 'https://api.empresa.pt',
    title: '{{ shop.name }}',
    primaryColor: '{{ settings.colors_accent_1 }}'
  });
</script>
```

### React

```jsx
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://api.empresa.pt/widget/aiti-widget.js';
    script.onload = () => {
      window.AITIWidget.init({
        apiUrl: 'https://api.empresa.pt'
      });
    };
    document.body.appendChild(script);
  }, []);

  return <div>...</div>;
}
```
