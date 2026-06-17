import { useState } from 'react';
import { RefreshCw, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function SteamSyncCard({ onSyncComplete }) {
  const [steamId, setSteamId] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [status, setStatus] = useState(null); // 'success' ou 'error'

  const handleSync = async () => {
    if (!steamId) return;
    setLoading(true);
    setMessage(null);

    try {
      const token = localStorage.getItem('token'); 
      const response = await fetch(`http://127.0.0.1:8000/sync/steam?player_id_externo=${steamId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        }
      });

      const data = await response.json();

      if (response.ok) {
        setStatus('success');
        setMessage(data.mensagem);
        setSteamId('');
        if (onSyncComplete) onSyncComplete(); // Pra recarregar bibliotecawwwwwwww
      } else {
        setStatus('error');
        setMessage(data.detail || 'Erro ao sincronizar.');
      }
    } catch (error) {
      setStatus('error');
      setMessage('Falha ao conectar com o servidor.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 rounded-3xl border border-white/10 bg-white/[0.02] mb-8 relative overflow-hidden">
      
      <div className="absolute -right-20 -top-20 w-64 h-64 bg-blue-600/10 blur-[80px] rounded-full pointer-events-none" />
      
      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h3 className="text-white font-bold text-lg mb-1 flex items-center gap-2">
            Sincronização com a Steam
          </h3>
          <p className="text-white/50 text-sm max-w-md">
            Gostaria de importar seus jogos da Steam? Insira o seu ID Público de 17 dígitos abaixo e importe toda a sua biblioteca para o NOCTIS em segundos.
          </p>
        </div>

        <div className="flex flex-col gap-2 w-full md:w-auto">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={steamId}
              onChange={(e) => setSteamId(e.target.value.replace(/\D/g, ''))}
              placeholder="Ex: 76561198000000000"
              className="bg-black/50 border border-white/10 text-white px-4 py-3 rounded-xl focus:outline-none focus:border-blue-500/50 w-full md:w-64 text-sm transition-colors"
            />
            <button
              onClick={handleSync}
              disabled={loading || steamId.length < 15}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-50 text-white px-5 py-3 rounded-xl font-semibold text-sm flex items-center gap-2 transition-all"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : 'Sincronizar'}
            </button>
          </div>
          
          {message && (
            <div className={`flex items-center gap-2 text-xs font-medium mt-1 ${status === 'success' ? 'text-green-400' : 'text-red-400'}`}>
              {status === 'success' ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
              {message}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}