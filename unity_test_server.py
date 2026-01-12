# unity_test_server.py
import asyncio
import json
import websockets
import time

# Mantemos um buffer por conexão para agrupar avaliações por geração
async def handler(ws, path=None):
    print("Client connected")
    try:
        buffer_by_gen = {}
        async for msg in ws:
            try:
                data = json.loads(msg)
            except Exception:
                continue

            if data.get("type") == "evaluate":
                gen = data.get("generation", 0)
                idx = data.get("id")
                genes = data.get("genes", [])
                # Simula trabalho curto por indivíduo
                time.sleep(0.02)
                fitness = sum(genes)

                # guarda no buffer
                if gen not in buffer_by_gen:
                    buffer_by_gen[gen] = {}
                buffer_by_gen[gen][int(idx)] = float(fitness)
                print(f"Received evaluate gen={gen} id={idx} -> fitness={fitness:.6f}")

                continue

            if data.get("type") == "evaluate_done":
                gen = data.get("generation", 0)
                pop_size = int(data.get("pop_size", 0))
                gen_buffer = buffer_by_gen.get(gen, {})
                # se não tivermos todos, podemos esperar um pouco e depois enviar o que temos
                # aqui fazemos uma espera curta para permitir chegarem mensagens pendentes
                await asyncio.sleep(0.05)
                gen_buffer = buffer_by_gen.get(gen, gen_buffer)
                # monta lista ordenada por id com (id, fitness)
                results = []
                for i in range(pop_size):
                    fitness = gen_buffer.get(i, None)
                    # se faltar algum, colocamos null (ou 0.0) — preferimos null para detectar erros
                    results.append({"id": i, "fitness": fitness})
                resp = {"type": "results_batch", "generation": gen, "results": results}
                await ws.send(json.dumps(resp))
                print(f"Sent results_batch gen={gen} count={len(results)}")
                # opcional: limpar buffer para essa geração
                buffer_by_gen.pop(gen, None)
                continue

    except websockets.ConnectionClosed:
        print("Client disconnected")
    except Exception as e:
        print("Handler error:", e)

async def main():
    server = await websockets.serve(handler, "localhost", 8765)
    print("Unity test server running on ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
