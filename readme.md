**GameMind AI**<br><br> 

**Descripción del problema** 

Elegir videojuegos adecuados o similares a otros juegos suele ser una tarea difícil para los usuarios, ya que las recomendaciones en tiendas digitales como Steam son limitadas, poco personalizadas o demasiado genéricas. 

 GameMind AI resuelve este problema creando un asistente inteligente que: 

*   Permite buscar información detallada de videojuegos 
    
*   Recomienda juegos similares basándose en géneros, tags y experiencia de jugadores 
    
*   Ofrece recomendaciones incluso cuando las APIs externas fallan mediante un sistema de respaldo basado en RAG (Retrieval-Augmented Generation) 
    

El objetivo es proporcionar recomendaciones más precisas, explicables y robustas que las típicas sugerencias automáticas de plataformas de juegos.<br><br> 

**Integración de IA en el sistema** 

El núcleo del sistema es un agente basado en LLM (ChatOllama) que actúa como orquestador de herramientas. 

El modelo no responde directamente al usuario, sino que: 

1\. Analiza la intención del usuario 

2\. Decide qué herramienta usar 

3\. Procesa la información devuelta 

4\. Genera una respuesta final coherente<br><br> 

**Herramientas del agente** 

El sistema dispone de 3 tools principales:<br> 

1. search\_game\_tool: Consulta la API oficial de Steam y devuelve 

*   Nombre del juego  
    
*   Géneros  
    
*   Tags  
    
*   Descripción  
    
*   Desarrollador  
    
*   Fecha de lanzamiento<br> 
    

2. recommend\_games\_tool: Consulta el api SteamSpy  y recomienda juegos basados en tags de género aplicando un sistema de ranking: 

*   coincidencia de tags  
    
*   reviews positivas/negativas  
    
*   score de SteamSpy
    

También filtra contenido NSFW<br> 

3. game\_profile\_rag\_tool: 
El game profile RAG tool es un sistema RAG que utiliza reseñas reales de jugadores para generar respuestas basadas en la sensación de juego. Funciona mediante embeddings creados con _sentence_‑_transformers_ y almacena la información en una base vectorial construida con ChromaDB. Este sistema se activa como mecanismo de respaldo cuando fallan APIs externas o cuando se requiere una evaluación más subjetiva y matizada sobre la experiencia del jugador.<br><br> 

**Arquitectura general** 

El sistema sigue una arquitectura modular basada en agente + tools + backend de datos.<br> 

**Componentes principales** 

El sistema se compone de un frontend desarrollado con Gradio, que actúa como interfaz principal del usuario. Desde ahí, las solicitudes pasan al agente construido con LangChain y ChatOllama, encargado de coordinar la lógica conversacional y decidir qué herramienta utilizar en cada caso. Este agente se apoya en una capa de herramientas que incluye tres módulos principales: el Steam API Tool, el SteamSpy Tool y el RAG Semantic Tool. Finalmente, todo el sistema se sustenta en un backend de datos compuesto por la Steam Web API, la SteamSpy API y una base vectorial en ChromaDB que almacena embeddings generados a partir de reseñas de jugadores.<br> 

**Flujo del agente** 

Caso 1: Usuario busca un juego concreto 

1.  search\_game\_tool  
    
2.  Devuelve información estructurada del juego  
    
3.  El LLM la resume<br>
    

Caso 2: Juegos similares a otro juego 

1.  search\_game\_tool → obtiene tags del juego 
    
2.  recommend\_games\_tool → genera recomendaciones 
    
3.  Si falla -> game\_profile\_rag\_tool (fallback semántico)
    

Caso 3: Fallo de APIs 

*   Si Steam o SteamSpy fallan se activa el sistema RAG local 
    
*   Si también falla el agente informa al usuario sin inventar resultados<br><br> 
    

**Tecnologías utilizadas** 

Inteligencia Artificial 

*   LangChain 
    
*   ChatOllama (modelo local: Qwen 3 8B) 
    
*   Sentence Transformers (embeddings) 
    

APIs externas 

*   Steam Web API 
    
*   SteamSpy API 
    

Sistema RAG 

*   ChromaDB (vector database) 
    
*   HuggingFace embeddings 
    

Backend 

*   Python 3.10+ 
    
*   Requests 
    
*   Logging 
    

Frontend 

*   Gradio (ChatInterface)<br><br> 

**Ejecución en local** 

1.Clonar el repositorio 

*   git clone [https://github.com/tuusuario/gamemind-ai.git](https://github.com/tuusuario/gamemind-ai.git) 

*   cd gamemind-ai 

2\. Crear entorno virtual 

*   python -m venv venv 

*   source venv/bin/activate   # Linux / Mac 

*   venv\\Scripts\\activate      # Windows 

3. Instalar dependencias 

*   pip install -r requirements.txt 

4\. Generar base de datos RAG 

*   python ingest\_reviews.py 

5. Ejecutar la aplicación 

*   python app.py 

6. Abrir en el navegador 

*   http://localhost:7860<br><br>  


**Reflexión final**<br>
El proyecto ha probado ser un gran reto y cuanta con varias limitaciones. La principal dificultad ha sido la naturaleza del LLM al decidir qué herramienta utilizar, lo que en ocasiones genera selecciones con inconsistencias en el flujo del agente.  
También he encontrado problemas en la integración con APIs externas como Steam y SteamSpy, especialmente cuando los datos devueltos no son totalmente precisos o están mal interpretados por el modelo, por ejemplo, al preguntarle por el juego The Witcher 3 no era capaz de diferenciar entre el juego y una herramienta del juego. Steam Spy en concreto ha sido un dolor de cabeza, la api empezó funcionando sin mucho problema, pero de vez en cuando deja de hacerlo, es muy poco fiable en ese sentido. Debido a esto tuve que hacer que hacer que si la api usada para las recomendaciones falla, la recomendación del juego recayera en el game profile RAG tool y se avise al usuario de que la api está caída. 

 

Como mejoras futuras, me gustaría reforzar el filtrado y limpieza de datos provenientes de APIs externas, y mejorar el sistema RAG para que actúe como un verdadero respaldo semántico más fiable. También me gustaría escalar la arquitectura hacia un sistema  con mejor separación entre lógica, herramientas e interfaz. Además si es posible me gustaría encontrar e implementar una api más estable, lo que me permitiría añadir más funcionalidades, además de que estas serían más fiables.  Funcionalidades como enviar las recomendaciones de juegos junto a los links de sus páginas principales de Steam, añadir límite de precio, región, y búsqueda de contenido adicional para juegos concretos. 
 

 

 

 

 

 
