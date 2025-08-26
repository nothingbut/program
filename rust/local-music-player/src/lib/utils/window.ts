import { getCurrentWindow } from '@tauri-apps/api/window';

/**
 * Update the window title
 */
export async function updateWindowTitle(title: string) {
  try {
    const appWindow = getCurrentWindow();
    await appWindow.setTitle(title);
  } catch (error) {
    console.warn('Failed to update window title:', error);
  }
}

/**
 * Set window title based on current track and app state
 */
export async function setDynamicTitle(appTitle: string, currentTrack?: { title: string; artist: string }) {
  let title = appTitle;
  
  if (currentTrack) {
    title = `${currentTrack.title} - ${currentTrack.artist} | ${appTitle}`;
  }
  
  await updateWindowTitle(title);
}