import { TestBed } from '@angular/core/testing';

import { RadarFeedService } from './radar-feed.service';

describe('RadarFeedService', () => {
  let service: RadarFeedService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RadarFeedService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
