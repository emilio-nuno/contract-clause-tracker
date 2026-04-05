import { Component, inject, signal } from '@angular/core';
import { MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { ApiService } from '../../../services/api';

@Component({
  selector: 'app-upload-dialog',
  templateUrl: './upload-dialog.html',
  styleUrl: './upload-dialog.css',
  imports: [MatDialogModule, MatButtonModule, MatIconModule],
})
export class UploadDialog {
  private api = inject(ApiService);
  private dialogRef = inject(MatDialogRef<UploadDialog>);

  selectedFile = signal<File | null>(null);
  uploading = signal(false);
  error = signal('');

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    this.selectedFile.set(input.files?.[0] ?? null);
    this.error.set('');
  }

  upload() {
    const file = this.selectedFile();
    if (!file) return;
    this.uploading.set(true);
    this.error.set('');
    this.api.uploadContract(file).subscribe({
      next: () => this.dialogRef.close(true),
      error: err => {
        this.error.set(err.error?.detail ?? 'Upload failed.');
        this.uploading.set(false);
      },
    });
  }
}
