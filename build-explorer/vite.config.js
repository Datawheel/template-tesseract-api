import legacy from "@vitejs/plugin-legacy";

const serverUrl = `/tesseract/`;

/** @type {import("vite").UserConfig} */
const config = {
  base: "",
  build: {
    outDir: "../static/",
    minify: "terser",
    rollupOptions: {
      output: {
        manualChunks: {
          extras: [
            "@mantine/dates",
            "dayjs",
          ],
        },
      },
    },
  },
  clearScreen: false,
  define: {
    'process.env.__SERVER_LOCALE__': JSON.stringify(`en,es,fr`),
    'process.env.__SERVER_URL__': JSON.stringify(serverUrl),
    'process.env.__UI_LOCALE__': JSON.stringify(`en`),
  },
  plugins: [
    legacy({
      targets: ['defaults', 'not IE 11']
    })
  ],
  server: {
    proxy: {
      [serverUrl]: {
        target: "http://localhost:7777/tesseract/",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/tesseract/, '')
      }
    }
  }
};

export default config
