# BoardBuy UAE — Database Schema Reference

All tables live in `backend/api/models.py` (PostgreSQL 16 + PostGIS).
After changes run: `manage.py makemigrations && manage.py migrate`.

## Record groups → tables

### 1. Users and companies
| Table | Purpose | Key fields |
|---|---|---|
| `User` | All logins, role-based | role (advertiser/owner/admin), phone |
| `MediaCompany` | Billboard owner | trade_licence, TRN, IBAN, licence_doc, status (pending→approved), commission_pct override |
| `Advertiser` | Advertiser account | company_name, TRN, status |

### 2. Billboard locations
| `Unit` | One billboard | **location: PostGIS Point (GPS)**, emirate, area, facing, status (pending→verified) |
| `UnitPhoto` | Gallery | image, sort |

### 3. Media formats & screen specifications
| `MediaFormat` | Admin-managed format catalogue | code, is_digital, requires_production |
| `ScreenSpec` | Digital unit tech specs (1:1 Unit) | resolution px, pixel pitch, slot/loop seconds, slots_per_loop |

### 4. Prices and availability
| `Unit` (pricing cols) | price_daily / price_weekly / price_monthly (AED) |
| `AvailabilitySlot` | Owner calendar | unit, start, end, is_blocked; bookings lock overlaps |

### 5. Campaigns and bookings
| `Campaign` | Advertiser's campaign container | name, start, end |
| `Booking` | One unit in a campaign | status machine: quote→requested→accepted→deposit_paid→paid→installing→live→completed; media_price, commission_pct, vat_pct; computed total & owner_payout |

### 6. Advertiser artwork
| `Creative` | Uploaded artwork per booking | file, status (pending/approved/rejected), review_note |

### 7. Quotations and contracts
| `Quotation` | Formal quote | number, subtotal/vat/total, valid_until, status, pdf |
| `QuotationItem` | Line items | unit, dates, price |
| `Contract` | Signed agreement (1:1 Booking) | number, file, sent_at, signed_at, signed_by_name |

### 8. Invoices and payments
| `Invoice` | Balance per booking (1:1) | number, amount, amount_paid, gateway_ref, status |
| `Payment` | Transaction ledger | kind (deposit/balance/full/refund/**payout** to owner), gateway, gateway_ref, status, paid_at |

### 9. Installation evidence
| `PlayProof` | Photos per booking | kind: install / display, image, taken_at — both kinds present flips Booking→live |

### 10. Campaign impressions and reports
| `ImpressionRecord` | Daily audience per booking | date, impressions, plays (digital), source (traffic_model/sensor/provider) |
| `CampaignReport` | Periodic rollup | totals, pdf, generated_at |

### 11. Reviews, notifications, support
| `Review` | Post-campaign rating (1:1 Booking) | rating 1–5, comment, is_public |
| `Notification` | Multi-channel | channel (in_app/email/whatsapp/sms), title, link, is_read |
| `SupportTicket` | Ticketing | number, topic, status (open/pending/closed), priority, optional booking link |
| `TicketMessage` | Thread | author, body, attachment |
| `Dispute` | Refund/claim cases | claim_amount, resolution (full/partial refund, date credit, denied) |

## Relationship map

```
User 1—1 MediaCompany 1—* Unit 1—1 ScreenSpec
                              1—* UnitPhoto
                              1—* AvailabilitySlot
User 1—1 Advertiser 1—* Campaign 1—* Booking *—1 Unit
                        1—* Quotation 1—* QuotationItem
Booking 1—1 Contract        Booking 1—1 Invoice 1—* Payment
Booking 1—* Creative        Booking 1—* PlayProof
Booking 1—* ImpressionRecord   Campaign 1—* CampaignReport
Booking 1—1 Review          Booking 1—* Dispute
User 1—* Notification       User 1—* SupportTicket 1—* TicketMessage
```
