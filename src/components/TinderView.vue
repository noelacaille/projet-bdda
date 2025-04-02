<template>
    <div class="tinder-container">
      <div v-if="currentGame" class="game-card">
        <img :src="currentGame.image" :alt="currentGame.name" class="game-image" />
        <h3>{{ currentGame.name }}</h3>
        <p>{{ currentGame.description }}</p>
        <div class="buttons">
          <button @click="dislike">❌</button>
          <button @click="like">❤️</button>
        </div>
      </div>
      <div v-else>
        <p>Plus de jeux à afficher</p>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const games = ref([
    { id: 1, name: "Catan", description: "Un jeu de stratégie populaire.", image: "https://example.com/catan.jpg" },
    { id: 2, name: "Carcassonne", description: "Posez des tuiles et construisez votre royaume.", image: "https://example.com/carcassonne.jpg" },
    { id: 3, name: "7 Wonders", description: "Construisez votre civilisation.", image: "https://example.com/7wonders.jpg" }
  ]);
  
  const currentIndex = ref(0);
  const currentGame = ref(games.value[currentIndex.value]);
  const likedGames = ref([]);
  
  const like = () => {
    likedGames.value.push(currentGame.value);
    nextGame();
  };
  
  const dislike = () => {
    nextGame();
  };
  
  const nextGame = () => {
    currentIndex.value++;
    if (currentIndex.value < games.value.length) {
      currentGame.value = games.value[currentIndex.value];
    } else {
      currentGame.value = null;
    }
  };
  </script>
  
  <style scoped>
  .tinder-container {
    text-align: center;
    margin: 20px;
  }
  .game-card {
    border: 1px solid #ccc;
    border-radius: 10px;
    padding: 20px;
    display: inline-block;
  }
  .game-image {
    width: 200px;
    height: auto;
    border-radius: 10px;
  }
  .buttons {
    margin-top: 10px;
  }
  button {
    font-size: 24px;
    margin: 0 10px;
    padding: 10px;
    cursor: pointer;
    border: none;
    background-color: transparent;
  }
  </style>
  