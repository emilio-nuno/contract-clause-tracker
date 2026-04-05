import { Component, inject } from '@angular/core';
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

  selectedFile: File | null = null;
  uploading = false;
  error = '';

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    this.selectedFile = input.files?.[0] ?? null;
    this.error = '';
  }

  upload() {
    if (!this.selectedFile) return;
    this.uploading = true;
    this.error = '';
    this.api.uploadContract(this.selectedFile).subscribe({
      next: () => this.dialogRef.close(true),
      error: err => {
        this.error = err.error?.detail ?? 'Upload failed.';
        this.uploading = false;
      },
    });
  }
}
