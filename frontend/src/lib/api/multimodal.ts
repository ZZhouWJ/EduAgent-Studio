import client from "./client";

export interface ImageUnderstandResult {
  success: boolean;
  content: string;
  error: string;
}

export const multimodalApi = {
  understandImage(file: Blob, filename: string, question: string) {
    const formData = new FormData();
    formData.append("file", file, filename);
    formData.append("question", question);
    return client.post<ImageUnderstandResult>("/multimodal/image/understand", formData);
  },
};
